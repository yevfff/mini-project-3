from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect

from typing import List
from sqlalchemy.orm import Session
from .. import models, schemas, database
from ..oauth2 import get_current_user, get_user_from_token, get_access_token, get_access_token_for_websocket
from datetime import datetime

router = APIRouter()

@router.get("/chats", response_model=List[schemas.ChatSummary])
def get_user_chats(current_user: int = Depends(get_current_user), db: Session = Depends(database.get_db)):
    chats = db.query(models.ChatMessage).filter(
        (models.ChatMessage.sender_id == current_user) | 
        (models.ChatMessage.recipient_id == current_user)
    ).all()

    if not chats:
        raise HTTPException(status_code=404, detail="No chats found")

    chat_summaries = []
    for chat in chats:
        partner_id = chat.sender_id if chat.sender_id != current_user else chat.recipient_id
        last_message = db.query(models.ChatMessage).filter(
            ((models.ChatMessage.sender_id == current_user) & (models.ChatMessage.recipient_id == partner_id)) | 
            ((models.ChatMessage.sender_id == partner_id) & (models.ChatMessage.recipient_id == current_user))
        ).order_by(models.ChatMessage.timestamp.desc()).first()
        
        chat_summaries.append(schemas.ChatSummary(
            partner_id=partner_id,
            last_message=last_message.content if last_message else "No messages",
            timestamp=last_message.timestamp if last_message else datetime.utcnow()
        ))

    return chat_summaries




class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: dict = {}  

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_connections[user_id] = websocket  

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        for user_id, ws in self.user_connections.items():
            if ws == websocket:
                del self.user_connections[user_id] 

    async def send_personal_message(self, websocket: WebSocket, message: str):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = WebSocketManager()


@router.get("/chat_messages/{partner_id}", response_model=List[schemas.ChatMessage])
def get_chat_messages(partner_id: int, current_user: int = Depends(get_current_user), db: Session = Depends(database.get_db)):
    chat_messages = db.query(models.ChatMessage).filter(
        ((models.ChatMessage.sender_id == current_user.id) & (models.ChatMessage.recipient_id == partner_id)) | 
        ((models.ChatMessage.sender_id == partner_id) & (models.ChatMessage.recipient_id == current_user.id))
    ).order_by(models.ChatMessage.timestamp).all()


    if not chat_messages:
        raise HTTPException(status_code=404, detail="No messages found")

    return chat_messages


# @router.websocket("/chat/{partner_id}")
# async def chat_websocket(websocket: WebSocket, partner_id: int, token: str = Depends(get_access_token_for_websocket), db: Session = Depends(database.get_db)):
#     print(f"Received token: {token}") 
#     try:
#         user = await get_user_from_token(token, db)  
#     except HTTPException as e:
#         await websocket.close(code=1008)  
#         print("Invalid token:", e.detail)
#         return
#     await manager.connect(websocket, user.id)
    
#     try:
#         while True:
#             data = await websocket.receive_text()
#             print(f"Received message: {data}")  # Debugging line
#             db_message = models.ChatMessage(sender_id=user.id, recipient_id=partner_id, content=data, timestamp=datetime.utcnow())
#             db.add(db_message)
#             db.commit()

#             # Send the message to all active WebSocket connections
#             for connection in manager.active_connections:
#                 if connection.client_state == 'CONNECTED':  # Check for the active connection
#                     await connection.send_text(f"{user.username}: {data}")

#     except WebSocketDisconnect:
#         print(f"User {user.id} disconnected")  # Debugging line
#         manager.disconnect(user.id)




@router.websocket("/chat/{partner_id}")
async def chat_websocket(websocket: WebSocket, partner_id: int, token: str = Depends(get_access_token_for_websocket), db: Session = Depends(database.get_db)):
    try:
        user = await get_user_from_token(token, db)
    except HTTPException as e:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, user.id)

    try:
        while True:
            content = await websocket.receive_text()
            db_message = models.ChatMessage(
                sender_id=user.id, recipient_id=partner_id, content=content, timestamp=datetime.utcnow()
            )
            db.add(db_message)
            db.commit()

            username = user.username
            for connection in manager.active_connections:
                await connection.send_text(f"{username}: {content}")

    except WebSocketDisconnect:
        await manager.disconnect(websocket)



