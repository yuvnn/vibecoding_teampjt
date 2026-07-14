from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChatRoomCreate(BaseModel):
    session_uuid: str = Field(min_length=1)


class ChatRoomOut(BaseModel):
    room_id: int
    session_uuid: str
    created_at: datetime


class ChatMessageCreate(BaseModel):
    message: str = Field(min_length=1)


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sender: str
    message: str
    created_at: datetime


class ChatSendResponse(BaseModel):
    user_message: ChatMessageOut
    bot_response: ChatMessageOut


class ChatHistoryOut(BaseModel):
    room_id: int
    messages: list[ChatMessageOut]
