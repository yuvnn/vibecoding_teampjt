from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.chat_message import ChatMessage
from app.models.chat_room import ChatRoom
from app.schemas.chatbot import (
    ChatHistoryOut,
    ChatMessageCreate,
    ChatRoomCreate,
    ChatRoomOut,
    ChatSendResponse,
)
from app.services.chatbot_service import send_message

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])


@router.post("/rooms", response_model=ChatRoomOut, status_code=201)
def create_room(payload: ChatRoomCreate, db: Session = Depends(get_db)):
    room = db.execute(
        select(ChatRoom).where(ChatRoom.session_uuid == payload.session_uuid)
    ).scalar_one_or_none()
    if not room:
        room = ChatRoom(session_uuid=payload.session_uuid)
        db.add(room)
        db.commit()
        db.refresh(room)
    return ChatRoomOut(room_id=room.id, session_uuid=room.session_uuid, created_at=room.created_at)


@router.post("/rooms/{room_id}/messages", response_model=ChatSendResponse)
def post_message(room_id: int, payload: ChatMessageCreate, db: Session = Depends(get_db)):
    room = db.get(ChatRoom, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="대화방을 찾을 수 없습니다.")
    user_message, bot_message = send_message(db, room, payload.message)
    return ChatSendResponse(user_message=user_message, bot_response=bot_message)


@router.get("/rooms/{room_id}/messages", response_model=ChatHistoryOut)
def get_history(room_id: int, db: Session = Depends(get_db)):
    room = db.get(ChatRoom, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="대화방을 찾을 수 없습니다.")
    messages = (
        db.execute(
            select(ChatMessage)
            .where(ChatMessage.room_id == room_id)
            .order_by(ChatMessage.created_at)
        )
        .scalars()
        .all()
    )
    return ChatHistoryOut(room_id=room_id, messages=messages)
