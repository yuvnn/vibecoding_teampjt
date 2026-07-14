from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _not_blank(value: str) -> str:
    if not value.strip():
        raise ValueError("공백만으로는 입력할 수 없습니다.")
    return value


class PostCreate(BaseModel):
    category_id: int
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    password: str = Field(min_length=1)

    _validate = field_validator("title", "content", "password")(_not_blank)


class PostUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    password: str = Field(min_length=1)

    _validate = field_validator("title", "content", "password")(_not_blank)


class PasswordCheck(BaseModel):
    password: str = Field(min_length=1)


class PostOut(BaseModel):
    """POST/PUT 응답 — 목록용 category_name은 포함하지 않는다."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    title: str
    content: str
    view_count: int
    created_at: datetime


class PostDetailOut(PostOut):
    """GET 단건 조회 응답 — category_name 포함."""

    category_name: str


class PostListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    title: str
    view_count: int
    created_at: datetime


class PostListResponse(BaseModel):
    total_count: int
    page: int
    limit: int
    posts: list[PostListItem]
