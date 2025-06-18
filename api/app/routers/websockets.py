# Path: api/app/routers/websockets.py
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Optional
import json
import random 

from app.db.database import get_db
from app.models.user import User as UserModel
from app.models.campaign import Campaign as CampaignModel
from app.routers.auth import get_user_from_websocket_token

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # active_connections maps: { campaign_id: { user_id: WebSocket } }
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}
        # NEW: In-memory store for the initiative text for each campaign
        self.initiative_texts: Dict[int, str] = {}

    async def connect(self, websocket: WebSocket, campaign_id: int, user: UserModel):
        await websocket.accept()
        if campaign_id not in self.active_connections:
            self.active_connections[campaign_id] = {}
        self.active_connections[campaign_id][user.id] = websocket
        print(f"User '{user.username}' connected to campaign {campaign_id}.")

    def disconnect(self, campaign_id: int, user: UserModel):
        if campaign_id in self.active_connections and user.id in self.active_connections[campaign_id]:
            del self.active_connections[campaign_id][user.id]
            print(f"User '{user.username}' disconnected from campaign {campaign_id}.")
            # If the room is now empty, clear its initiative text from memory
            if not self.active_connections[campaign_id]:
                del self.active_connections[campaign_id]
                if campaign_id in self.initiative_texts:
                    del self.initiative_texts[campaign_id]

    async def broadcast_json(self, data: dict, campaign_id: int, exclude_websocket: Optional[WebSocket] = None):
        if campaign_id in self.active_connections:
            for connection in self.active_connections[campaign_id].values():
                if connection is not exclude_websocket:
                    try:
                        await connection.send_json(data)
                    except Exception as e:
                        print(f"Failed to send message: {e}")

manager = ConnectionManager()

@router.websocket("/ws/campaign/{campaign_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    campaign_id: int,
    user: UserModel = Depends(get_user_from_websocket_token),
    db: AsyncSession = Depends(get_db)
):
    await manager.connect(websocket, campaign_id, user)
    
    # Announce user join to everyone
    join_message = {"type": "user_join", "sender": "System", "payload": f"User '{user.username}' has joined."}
    await manager.broadcast_json(join_message, campaign_id)

    # Send the current initiative text ONLY to the newly connected user
    if campaign_id in manager.initiative_texts:
        await websocket.send_json({
            "type": "initiative_text_update",
            "payload": {"text": manager.initiative_texts[campaign_id]}
        })

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            message_data['sender'] = user.username

            campaign = await db.get(CampaignModel, campaign_id)
            is_dm = campaign and campaign.dm_user_id == user.id

            # --- UPDATED LOGIC ---
            if message_data['type'] == 'dice_roll' or message_data['type'] == 'chat':
                await manager.broadcast_json(message_data, campaign_id)

            elif message_data['type'] == 'initiative_text_update' and is_dm:
                # Get the text from the DM's message
                text = message_data.get('payload', {}).get('text', '')
                # Store it on the server
                manager.initiative_texts[campaign_id] = text
                # Broadcast the update to everyone else
                await manager.broadcast_json(message_data, campaign_id, exclude_websocket=websocket)
            
            # --- END UPDATED LOGIC ---

    except WebSocketDisconnect:
        pass # Let the finally block handle cleanup
    except Exception as e:
        print(f"An error occurred in websocket for campaign {campaign_id}: {e}")
    finally:
        manager.disconnect(campaign_id, user)
        leave_message = {"type": "user_leave", "sender": "System", "payload": f"User '{user.username}' has left."}
        await manager.broadcast_json(leave_message, campaign_id)
