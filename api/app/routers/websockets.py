# Path: api/app/routers/websockets.py
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict
from fastapi.responses import JSONResponse
import json
import random 

from app.db.database import get_db
from app.models.user import User as UserModel
from app.routers.auth import get_current_active_user
from app.crud import crud_user
from app.routers.auth import get_token_from_query
from app.core.security import verify_token_and_get_token_data

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, campaign_id: int, user_id: int):
        await websocket.accept()
        if campaign_id not in self.active_connections:
            self.active_connections[campaign_id] = {}
        self.active_connections[campaign_id][user_id] = websocket
        print(f"User {user_id} connected to campaign {campaign_id}.")

    def disconnect(self, campaign_id: int, user_id: int):
        if campaign_id in self.active_connections and user_id in self.active_connections[campaign_id]:
            del self.active_connections[campaign_id][user_id]
            print(f"User {user_id} disconnected from campaign {campaign_id}.")
            if not self.active_connections[campaign_id]:
                del self.active_connections[campaign_id]

    async def broadcast_json(self, data: dict, campaign_id: int):
        if campaign_id in self.active_connections:
            for user_id, connection in self.active_connections[campaign_id].items():
                try:
                    await connection.send_json(data)
                except Exception as e:
                    print(f"Failed to send message to user {user_id}: {e}")


manager = ConnectionManager()


async def get_user_from_websocket_token(
    token: str = Query(...), 
    db: AsyncSession = Depends(get_db)
) -> UserModel:
    """Dependency to authenticate a user via a token in a WebSocket query param."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        token_data = verify_token_and_get_token_data(token, credentials_exception)
        if token_data.username is None:
            raise credentials_exception
    except Exception:
         raise credentials_exception
         
    user = await crud_user.get_user_by_username(db, username=token_data.username)
    if user is None or not user.is_active:
        raise credentials_exception
    return user


@router.websocket("/ws/campaign/{campaign_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    campaign_id: int,
    user: UserModel = Depends(get_user_from_websocket_token)
):
    """
    Main WebSocket endpoint for a campaign room.
    Authenticates using a token from the query parameters.
    """
    await manager.connect(websocket, campaign_id, user.id)
    
    join_message = {"type": "user_join", "sender": "System", "payload": f"User '{user.username}' has joined."}
    await manager.broadcast_json(join_message, campaign_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            message_data['sender'] = user.username
            
            # --- NEW: Dice Rolling Logic ---
            if message_data['type'] == 'dice_roll':
                try:
                    sides = int(message_data['payload']['sides'])
                    count = int(message_data['payload'].get('count', 1)) # Default to 1 die
                    rolls = [random.randint(1, sides) for _ in range(count)]
                    total = sum(rolls)
                    
                    # Prepare a rich payload for the dice roll result
                    message_data['payload'] = {
                        "sides": sides,
                        "count": count,
                        "rolls": rolls,
                        "total": total
                    }
                except (ValueError, KeyError) as e:
                    # Handle bad dice roll data
                    error_message = {"type": "error", "sender": "System", "payload": f"Invalid dice roll request: {e}"}
                    await websocket.send_json(error_message) # Send error only to the user who made it
                    continue
            # --- END NEW LOGIC ---

            await manager.broadcast_json(message_data, campaign_id)

    except WebSocketDisconnect:
        manager.disconnect(campaign_id, user.id)
        leave_message = {"type": "user_leave", "sender": "System", "payload": f"User '{user.username}' has left."}
        await manager.broadcast_json(leave_message, campaign_id)
    except Exception as e:
        print(f"An error occurred in websocket for campaign {campaign_id}: {e}")
        manager.disconnect(campaign_id, user.id)
