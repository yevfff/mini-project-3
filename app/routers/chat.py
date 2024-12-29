from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect, HTTPException, WebSocketException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
from app.database import get_db
from app.oauth2 import get_current_user
from app import models, schemas
from json.decoder import JSONDecodeError


router = APIRouter(
    prefix='/api',
    tags=["Chats"]
)

active_connections = {}


@router.websocket("/ws/chat/")
async def websocket_chat(websocket: WebSocket, db: Session = Depends(get_db)):
    try:
        token: str = websocket.headers.get("token")
        if not token:
            raise HTTPException(status_code=401, detail="Missing or invalid token")

        current_user = get_current_user(token=token, db=db)
    except WebSocketException as e:
        await websocket.close(code=1008, reason="Invalid authorization")
        return

    user_id = current_user.id
    await websocket.accept()
    active_connections[user_id] = websocket

    try:
        while True:
            try:
                data = await websocket.receive_json()
            except JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON format"})
                continue

            recipient_id = data.get("recipient_id")
            content = data.get("content")

            if not recipient_id or not content:
                await websocket.send_json({"error": "Invalid data"})
                continue

            chat_message = models.ChatMessage(
                sender_id=user_id,
                recipient_id=recipient_id,
                content=content
            )
            db.add(chat_message)
            db.commit()

            if recipient_id in active_connections:
                await active_connections[recipient_id].send_json({
                    "sender_id": user_id,
                    "content": content,
                    "timestamp": chat_message.timestamp.isoformat()
                })

    except WebSocketDisconnect:
        del active_connections[user_id]




@router.get("/chats", response_model=List[schemas.ChatSummary])
def get_user_chats(
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    user_id = current_user.id

    chats = db.query(models.ChatMessage).filter(
        or_(
            models.ChatMessage.sender_id == user_id,
            models.ChatMessage.recipient_id == user_id
        )
    ).distinct(models.ChatMessage.sender_id, models.ChatMessage.recipient_id).all()

    chat_summary = []
    for chat in chats:
        partner_id = chat.sender_id if chat.sender_id != user_id else chat.recipient_id
        last_message = db.query(models.ChatMessage).filter(
            or_(
                (models.ChatMessage.sender_id == user_id) & (models.ChatMessage.recipient_id == partner_id),
                (models.ChatMessage.sender_id == partner_id) & (models.ChatMessage.recipient_id == user_id)
            )
        ).order_by(models.ChatMessage.timestamp.desc()).first()

        chat_summary.append({
            "partner_id": partner_id,
            "last_message": last_message.content,
            "timestamp": last_message.timestamp
        })

    return chat_summary


@router.get("/chats/{recipient_id}", response_model=List[schemas.ChatMessage])
def get_chat_messages(
    recipient_id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    user_id = current_user.id

    messages = db.query(models.ChatMessage).filter(
        or_(
            (models.ChatMessage.sender_id == user_id) & (models.ChatMessage.recipient_id == recipient_id),
            (models.ChatMessage.sender_id == recipient_id) & (models.ChatMessage.recipient_id == user_id)
        )
    ).order_by(models.ChatMessage.timestamp).all()

    return messages