# Path: api/app/routers/websockets.py
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any, Optional
import json
import random 

from app.db.database import get_db
from app.models.user import User as UserModel
from app.models.campaign import Campaign as CampaignModel
from app.models.campaign_member import CampaignMember
from app.routers.auth import get_user_from_websocket_token

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
    
    # --- START FIX: Pre-fetch all necessary data ONCE on connect ---
    sender_name = user.username # Default sender name
    is_dm = False
    try:
        campaign = await db.get(
            CampaignModel, 
            campaign_id, 
            options=[selectinload(CampaignModel.members).selectinload(CampaignMember.character)]
        )
        if campaign:
            is_dm = campaign.dm_user_id == user.id
            my_member_record = next((m for m in campaign.members if m.user_id == user.id), None)
            if my_member_record and my_member_record.character:
                sender_name = my_member_record.character.name
    except Exception as e:
        print(f"Error fetching initial campaign data: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        manager.disconnect(campaign_id, user)
        return
    # --- END FIX ---
    
    await manager.broadcast_json({"type": "user_join", "sender": "System", "payload": {"text": f"'{sender_name}' has joined."}}, campaign_id)

    if campaign_id in manager.encounter_states:
        await websocket.send_json({"type": "encounter_update", "payload": manager.encounter_states[campaign_id]})

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Use pre-fetched sender name
            message_data['sender'] = sender_name

            if 'payload' in message_data and isinstance(message_data['payload'], dict):
                message_data['payload']['characterName'] = sender_name
            
            # --- START FIX: Process public messages first ---
            if message_data['type'] == 'dice_roll':
                payload = message_data['payload']
                try:
                    sides = int(payload['sides'])
                    count = int(payload.get('count', 1))
                    rolls = [random.randint(1, sides) for _ in range(count)]
                    payload['rolls'] = rolls
                    payload['total'] = sum(rolls)
                    await manager.broadcast_json(message_data, campaign_id)
                except (ValueError, KeyError):
                    await websocket.send_json({"type": "error", "payload": {"text": "Invalid dice roll request."}})

            elif message_data['type'] == 'chat':
                await manager.broadcast_json(message_data, campaign_id)
            # --- END FIX ---

            elif is_dm: # DM-only actions below
                current_encounter = manager.encounter_states.get(campaign_id, {})
                
                if message_data['type'] == 'start_encounter':
                    initiative_order = message_data.get('payload', [])
                    sorted_order = sorted(initiative_order, key=lambda x: x.get('roll', 0), reverse=True)
                    active_entry = sorted_order[0] if sorted_order else None
                    current_encounter = {
                        "is_active": True,
                        "turn_index": 0,
                        "order": sorted_order,
                        "active_entry_id": active_entry['id'] if active_entry else None
                    }
                    manager.encounter_states[campaign_id] = current_encounter
                    await manager.broadcast_json({"type": "encounter_update", "payload": current_encounter}, campaign_id)

                elif message_data['type'] == 'next_turn':
                    if current_encounter.get('is_active') and current_encounter.get('order'):
                        order = current_encounter['order']
                        current_encounter['turn_index'] = (current_encounter.get('turn_index', -1) + 1) % len(order)
                        current_encounter['active_entry_id'] = order[current_encounter['turn_index']]['id']
                        await manager.broadcast_json({"type": "encounter_update", "payload": current_encounter}, campaign_id)
                
                elif message_data['type'] == 'end_encounter':
                    if campaign_id in manager.encounter_states:
                        manager.encounter_states[campaign_id] = {"is_active": False, "order": [], "turn_index": -1, "active_entry_id": None}
                        await manager.broadcast_json({"type": "encounter_update", "payload": manager.encounter_states[campaign_id]}, campaign_id)
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"Websocket Error: {e}")
    finally:
        manager.disconnect(campaign_id, user)
        await manager.broadcast_json({"type": "user_leave", "sender": "System", "payload": {"text": f"'{sender_name}' has left."}}, campaign_id)

