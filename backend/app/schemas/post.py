from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _not_blank(value: str) -> str:
    if not value.strip():
        raise ValueError("공백만으로는 입력할 수 없습니다.")
    return value


class PostPlaceIn(BaseModel):
    place_name: str = Field(min_length=1, max_length=255)
    address: str | None = Field(default=None, max_length=255)
    map_x: float | None = None
    map_y: float | None = None


class PostPlaceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    place_name: str
    address: str | None
    map_x: float | None
    map_y: float | None


class PostCreate(BaseModel):
    category_ids: list[int] = Field(min_length=1)
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    password: str = Field(min_length=1)
    places: list[PostPlaceIn] = Field(default_factory=list)

    _validate = field_validator("title", "content", "password")(_not_blank)

    @field_validator("category_ids")
    @classmethod
    def _dedupe_categories(cls, value: list[int]) -> list[int]:
        deduped = list(dict.fromkeys(value))
        if not deduped:
            raise ValueError("카테고리를 하나 이상 선택해주세요.")
        return deduped


class PostUpdate(BaseModel):
    category_ids: list[int] = Field(min_length=1)
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    password: str = Field(min_length=1)
    places: list[PostPlaceIn] = Field(default_factory=list)

    _validate = field_validator("title", "content", "password")(_not_blank)

    @field_validator("category_ids")
    @classmethod
    def _dedupe_categories(cls, value: list[int]) -> list[int]:
        deduped = list(dict.fromkeys(value))
        if not deduped:
            raise ValueError("카테고리를 하나 이상 선택해주세요.")
        return deduped


class PasswordCheck(BaseModel):
    password: str = Field(min_length=1)


class PostOut(BaseModel):
    """POST/PUT 응답 — 목록용 category_names는 포함하지 않는다."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    category_ids: list[int]
    title: str
    content: str
    view_count: int
    places: list[PostPlaceOut]
    created_at: datetime


class PostDetailOut(PostOut):
    """GET 단건 조회 응답 — category_names 포함."""

    category_names: list[str]


class PostListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_ids: list[int]
    title: str
    view_count: int
    places: list[PostPlaceOut]
    created_at: datetime


class PostListResponse(BaseModel):
    total_count: int
    page: int
    limit: int
    posts: list[PostListItem]
