from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect

from typing import List
from sqlalchemy.orm import Session
from .. import models, schemas, database
from ..oauth2 import get_current_user, get_current_chat_user
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

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, websocket: WebSocket, message: str):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = WebSocketManager()


@router.get("/chat_messages/{partner_id}", response_model=List[schemas.ChatMessage])
def get_chat_messages(partner_id: int, current_user: int = Depends(get_current_user), db: Session = Depends(database.get_db)):
    chat_messages = db.query(models.ChatMessage).filter(
        ((models.ChatMessage.sender_id == current_user) & (models.ChatMessage.recipient_id == partner_id)) | 
        ((models.ChatMessage.sender_id == partner_id) & (models.ChatMessage.recipient_id == current_user))
    ).order_by(models.ChatMessage.timestamp).all()

    if not chat_messages:
        raise HTTPException(status_code=404, detail="No messages found")

    return chat_messages


@router.websocket("/chat/{partner_id}")
async def chat_websocket(websocket: WebSocket, partner_id: int):
    db = database.get_db()
    current_user = await get_current_chat_user(websocket, db)
    await manager.connect(websocket)

    try:
        while True:
            message = await websocket.receive_text()
            new_message = models.ChatMessage(
                sender_id=current_user.id, 
                recipient_id=partner_id,
                content=message,
                timestamp=datetime.utcnow()
            )
            db.add(new_message)
            db.commit()

            await manager.broadcast(f"User {current_user.id} says: {message}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"User {current_user.id} has left the chat.")

