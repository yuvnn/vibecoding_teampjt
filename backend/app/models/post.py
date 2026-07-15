from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # Legacy single-category/single-place columns — kept (and still written
    # to, mirroring the first entry of the new multi-value tables below) so
    # nothing that reads them directly breaks. post_categories/post_places
    # are the authoritative source of truth going forward.
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # 글쓰기에서 첨부한 장소(선택) — tour_items에서 고른 장소의 스냅샷을 저장한다.
    place_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    map_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    map_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    category = relationship("Category", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    post_categories = relationship(
        "PostCategory", back_populates="post", cascade="all, delete-orphan", order_by="PostCategory.id"
    )
    post_places = relationship(
        "PostPlace", back_populates="post", cascade="all, delete-orphan", order_by="PostPlace.id"
    )

    @property
    def category_ids(self) -> list[int]:
        return [pc.category_id for pc in self.post_categories]

    @property
    def category_names(self) -> list[str]:
        return [pc.category.name for pc in self.post_categories]

    @property
    def places(self) -> list["PostPlace"]:
        return self.post_places
