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
    region: str | None = None


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sender: str
    message: str
    created_at: datetime


class ChatPlaceRef(BaseModel):
    """RAG 검색으로 답변에 실제 인용된 장소. 프론트에서 '경로에 추가' 버튼을 그리는 데 쓴다."""

    content_id: str
    title: str
    addr1: str
    map_x: float | None
    map_y: float | None
    place_type: str


class ChatSendResponse(BaseModel):
    user_message: ChatMessageOut
    bot_response: ChatMessageOut
    referenced_places: list[ChatPlaceRef] = []


class ChatHistoryOut(BaseModel):
    room_id: int
    messages: list[ChatMessageOut]
