# Path: api/app/routers/websockets.py
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
import json
from sqlalchemy.orm import selectinload
from app.db.database import get_db
from app.models.user import User as UserModel
from app.models.campaign import Campaign as CampaignModel
from app.routers.auth import get_user_from_websocket_token
from app.schemas.initiative_entry import InitiativeEntryCreate

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}
        self.encounter_states: Dict[int, Dict[str, Any]] = {}

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
                if campaign_id in self.active_connections: del self.active_connections[campaign_id]
                if campaign_id in self.encounter_states: del self.encounter_states[campaign_id]

    async def broadcast_json(self, data: dict, campaign_id: int):
        if campaign_id in self.active_connections:
            for connection in self.active_connections[campaign_id].values():
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

    if campaign_id in manager.encounter_states:
        await websocket.send_json({"type": "encounter_update", "payload": manager.encounter_states[campaign_id]})

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Use character name if available, otherwise username
            my_member_record = next((m for m in (await db.get(CampaignModel, campaign_id, options=[selectinload(CampaignModel.members).selectinload("character")])).members if m.user_id == user.id), None)
            sender_name = my_member_record.character.name if my_member_record and my_member_record.character else user.username
            message_data['sender'] = sender_name

            if 'payload' in message_data and isinstance(message_data['payload'], dict):
                message_data['payload']['characterName'] = sender_name


            is_dm = (await db.get(CampaignModel, campaign_id)).dm_user_id == user.id

            if message_data['type'] in ['chat', 'dice_roll']:
                await manager.broadcast_json(message_data, campaign_id)

            elif is_dm:
                if message_data['type'] == 'start_encounter':
                    initiative_order = message_data['payload']
                    manager.encounter_states[campaign_id] = {
                        "is_active": True,
                        "turn_index": 0,
                        "order": sorted(initiative_order, key=lambda x: x['roll'], reverse=True)
                    }
                    await manager.broadcast_json({"type": "encounter_update", "payload": manager.encounter_states[campaign_id]}, campaign_id)

                elif message_data['type'] == 'next_turn':
                    if campaign_id in manager.encounter_states and manager.encounter_states[campaign_id]['is_active']:
                        current_state = manager.encounter_states[campaign_id]
                        current_state['turn_index'] = (current_state['turn_index'] + 1) % len(current_state['order'])
                        await manager.broadcast_json({"type": "encounter_update", "payload": current_state}, campaign_id)
                
                elif message_data['type'] == 'end_encounter':
                    if campaign_id in manager.encounter_states:
                        manager.encounter_states[campaign_id] = {"is_active": False, "order": [], "turn_index": -1}
                        await manager.broadcast_json({"type": "encounter_update", "payload": manager.encounter_states[campaign_id]}, campaign_id)
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"Websocket Error: {e}")
    finally:
        manager.disconnect(campaign_id, user)
        leave_message = {"type": "user_leave", "sender": "System", "payload": f"User '{user.username}' has left."}
        await manager.broadcast_json(leave_message, campaign_id)
