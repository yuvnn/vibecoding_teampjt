from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TourItem(Base):
    """공공데이터 내 개별 관광지/맛집/축제 등 상세 레코드."""

    __tablename__ = "tour_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    master_id: Mapped[int] = mapped_column(ForeignKey("tour_masters.id"), nullable=False)
    content_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    addr1: Mapped[str] = mapped_column(String(255), default="")
    addr2: Mapped[str] = mapped_column(String(255), default="")
    tel: Mapped[str] = mapped_column(String(50), default="")
    zipcode: Mapped[str] = mapped_column(String(10), default="")
    first_image: Mapped[str] = mapped_column(Text, default="")
    first_image2: Mapped[str] = mapped_column(Text, default="")
    map_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    map_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    m_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    area_code: Mapped[str] = mapped_column(String(10), default="")
    sigungu_code: Mapped[str] = mapped_column(String(10), default="")
    cat1: Mapped[str] = mapped_column(String(20), default="")
    cat2: Mapped[str] = mapped_column(String(20), default="")
    cat3: Mapped[str] = mapped_column(String(20), default="")
    created_time: Mapped[str] = mapped_column(String(20), default="")
    modified_time: Mapped[str] = mapped_column(String(20), default="")

    master = relationship("TourMaster", back_populates="items")
