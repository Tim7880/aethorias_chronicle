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
            if not self.active_connections.get(campaign_id):
                if campaign_id in self.encounter_states:
                    del self.encounter_states[campaign_id]
                if campaign_id in self.active_connections:
                    del self.active_connections[campaign_id]
        print(f"User '{user.username}' disconnected from campaign {campaign_id}.")

    async def broadcast_json(self, data: dict, campaign_id: int):
        if campaign_id in self.active_connections:
            for connection in self.active_connections[campaign_id].values():
                await connection.send_json(data)

manager = ConnectionManager()

# --- START FIX: Helper to build the correct encounter payload ---
def build_encounter_payload(encounter_state: Dict[str, Any]) -> Dict[str, Any]:
    """Safely builds the encounter payload for the frontend."""
    if not encounter_state or not encounter_state.get('is_active'):
        return {"is_active": False, "order": [], "active_entry_id": None}

    # The order is already sorted when it's created
    order_with_names = []
    for entry in encounter_state.get('order', []):
        is_character = entry.get('id', '').startswith('char_')
        name = entry.get('name', 'Unknown')
        order_with_names.append({
            "id": entry.get('id'),
            "name": name,
            "roll": entry.get('roll')
        })

    return {
        "is_active": True,
        "turn_index": encounter_state.get('turn_index', 0),
        "order": order_with_names,
        "active_entry_id": encounter_state.get('active_entry_id')
    }
# --- END FIX ---

@router.websocket("/ws/campaign/{campaign_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    campaign_id: int,
    user: UserModel = Depends(get_user_from_websocket_token),
    db: AsyncSession = Depends(get_db)
):
    await manager.connect(websocket, campaign_id, user)
    
    sender_name = user.username
    is_dm = False
    try:
        campaign = await db.get(CampaignModel, campaign_id, options=[selectinload(CampaignModel.members).selectinload(CampaignMember.character)])
        if campaign:
            is_dm = campaign.dm_user_id == user.id
            my_member_record = next((m for m in campaign.members if m.user_id == user.id), None)
            if my_member_record and my_member_record.character:
                sender_name = my_member_record.character.name
    except Exception as e:
        print(f"Error fetching initial campaign data: {e}")
        await manager.disconnect(campaign_id, user)
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        return
    
    await manager.broadcast_json({"type": "user_join", "sender": "System", "payload": {"text": f"'{sender_name}' has joined."}}, campaign_id)

    if campaign_id in manager.encounter_states:
        payload = build_encounter_payload(manager.encounter_states[campaign_id])
        await websocket.send_json({"type": "encounter_update", "payload": payload})

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            message_data['sender'] = sender_name

            if message_data['type'] in ['chat', 'dice_roll']:
                if message_data['type'] == 'dice_roll':
                    payload = message_data['payload']
                    sides = int(payload['sides'])
                    count = int(payload.get('count', 1))
                    rolls = [random.randint(1, sides) for _ in range(count)]
                    payload['rolls'] = rolls
                    payload['total'] = sum(rolls)
                await manager.broadcast_json(message_data, campaign_id)

            elif is_dm:
                current_encounter = manager.encounter_states.get(campaign_id, {})
                
                if message_data['type'] == 'start_encounter':
                    initiative_order = message_data.get('payload', [])
                    sorted_order = sorted(initiative_order, key=lambda x: x.get('roll', 0), reverse=True)
                    active_entry = sorted_order[0] if sorted_order else None
                    
                    # --- START FIX: Use 'initiative_entries' to match the frontend type ---
                    current_encounter = {
                        "is_active": True,
                        "turn_index": 0,
                        "initiative_entries": sorted_order,
                        "active_initiative_entry_id": active_entry['id'] if active_entry else None
                    }
                    # --- END FIX ---
                    manager.encounter_states[campaign_id] = current_encounter
                    await manager.broadcast_json({"type": "encounter_update", "payload": current_encounter}, campaign_id)

                elif message_data['type'] == 'next_turn':
                    if current_encounter.get('is_active') and current_encounter.get('order'):
                        order = current_encounter['order']
                        current_encounter['turn_index'] = (current_encounter.get('turn_index', -1) + 1) % len(order)
                        current_encounter['active_entry_id'] = order[current_encounter['turn_index']]['id']
                        await manager.broadcast_json({"type": "encounter_update", "payload": build_encounter_payload(current_encounter)}, campaign_id)
                
                elif message_data['type'] == 'end_encounter':
                    manager.encounter_states[campaign_id] = {"is_active": False, "order": [], "turn_index": -1, "active_entry_id": None}
                    await manager.broadcast_json({"type": "encounter_update", "payload": manager.encounter_states[campaign_id]}, campaign_id)
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"Websocket Error: {e}")
    finally:
        manager.disconnect(campaign_id, user)
        await manager.broadcast_json({"type": "user_leave", "sender": "System", "payload": {"text": f"'{sender_name}' has left."}}, campaign_id)

