# Path: api/app/routers/websockets.py
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Optional
import json
import random 

from app.db.database import get_db
from app.models.user import User as UserModel
from app.models.campaign import Campaign as CampaignModel
from app.crud import crud_user, crud_campaign_session
from app.schemas.initiative_entry import InitiativeEntryCreate
from app.routers.auth import get_user_from_websocket_token

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}

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
            if not self.active_connections[campaign_id]:
                del self.active_connections[campaign_id]

    async def broadcast_json(self, data: dict, campaign_id: int):
        if campaign_id in self.active_connections:
            connections = list(self.active_connections[campaign_id].values())
            for connection in connections:
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
    
    join_message = {"type": "user_join", "sender": "System", "payload": f"User '{user.username}' has joined."}
    await manager.broadcast_json(join_message, campaign_id)

    active_session = await crud_campaign_session.get_active_session_for_campaign(db, campaign_id=campaign_id)
    if active_session:
        initiative_order = await crud_campaign_session.get_initiative_order(db, session_id=active_session.id)
        initiative_payload = [entry.model_dump() for entry in initiative_order]
        await websocket.send_json({"type": "initiative_update", "payload": initiative_payload})

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            message_data['sender'] = user.username
            
            active_session = await crud_campaign_session.get_active_session_for_campaign(db, campaign_id=campaign_id)
            if not active_session:
                if message_data['type'] == 'chat':
                     await manager.broadcast_json(message_data, campaign_id)
                continue

            campaign = await db.get(CampaignModel, campaign_id)
            is_dm = campaign and campaign.dm_user_id == user.id

            if message_data['type'] == 'dice_roll':
                try:
                    sides = int(message_data['payload']['sides'])
                    count = int(message_data['payload'].get('count', 1))
                    rolls = [random.randint(1, sides) for _ in range(count)]
                    message_data['payload'] = { "sides": sides, "count": count, "rolls": rolls, "total": sum(rolls) }
                    await manager.broadcast_json(message_data, campaign_id)
                except Exception as e:
                    await websocket.send_json({"type": "error", "payload": f"Invalid dice roll: {e}"})

            elif message_data['type'] == 'chat':
                await manager.broadcast_json(message_data, campaign_id)

            elif message_data['type'] == 'add_initiative' and is_dm:
                try:
                    entry_schema = InitiativeEntryCreate(**message_data['payload'])
                    await crud_campaign_session.add_initiative_entry(db, session_id=active_session.id, entry_in=entry_schema)
                    updated_order = await crud_campaign_session.get_initiative_order(db, session_id=active_session.id)
                    initiative_payload = [entry.model_dump() for entry in updated_order]
                    await manager.broadcast_json({"type": "initiative_update", "payload": initiative_payload}, campaign_id)
                except Exception as e:
                    await websocket.send_json({"type": "error", "payload": f"Failed to add initiative: {e}"})

            elif message_data['type'] == 'clear_initiative' and is_dm:
                try:
                    await crud_campaign_session.clear_initiative(db, session_id=active_session.id)
                    await manager.broadcast_json({"type": "initiative_update", "payload": []}, campaign_id)
                except Exception as e:
                    await websocket.send_json({"type": "error", "payload": f"Failed to clear initiative: {e}"})
                
            elif message_data['type'] == 'next_turn' and is_dm:
                try:
                    next_active_entry = await crud_campaign_session.advance_turn(db, session_id=active_session.id)
                    await manager.broadcast_json({
                        "type": "turn_update",
                        "payload": {"active_entry_id": next_active_entry.id if next_active_entry else None}
                    }, campaign_id)
                except Exception as e:
                    await websocket.send_json({"type": "error", "payload": f"Failed to advance turn: {e}"})

    except WebSocketDisconnect:
        manager.disconnect(campaign_id, user)
        leave_message = {"type": "user_leave", "sender": "System", "payload": f"User '{user.username}' has left."}
        await manager.broadcast_json(leave_message, campaign_id)
    except Exception as e:
        print(f"An error occurred in websocket for campaign {campaign_id}: {e}")
        manager.disconnect(campaign_id, user)
