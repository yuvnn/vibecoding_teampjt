from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.tour_item import TourItem
from app.schemas.tour import TourItemDetail, TourItemListItem

router = APIRouter(prefix="/api/tour", tags=["tour"])


@router.get("/items/random", response_model=list[TourItemListItem])
def list_random_tour_items(
    content_type_id: int | None = None,
    region: str | None = None,
    count: int = 20,
    db: Session = Depends(get_db),
):
    query = select(TourItem)
    if content_type_id is not None:
        query = query.where(TourItem.master.has(content_type_id=content_type_id))
    if region:
        query = query.where(TourItem.master.has(region=region))

    query = query.order_by(func.random()).limit(min(max(count, 1), 100))
    return db.execute(query).scalars().all()


@router.get("/items", response_model=list[TourItemListItem])
def list_tour_items(
    content_type_id: int | None = None,
    region: str | None = None,
    keyword: str | None = None,
    sigungu_code: str | None = None,
    db: Session = Depends(get_db),
):
    query = select(TourItem)
    if content_type_id is not None:
        query = query.where(TourItem.master.has(content_type_id=content_type_id))
    if region:
        query = query.where(TourItem.master.has(region=region))
    if sigungu_code:
        query = query.where(TourItem.sigungu_code == sigungu_code)
    if keyword:
        like = f"%{keyword}%"
        query = query.where(or_(TourItem.title.ilike(like), TourItem.addr1.ilike(like)))

    return db.execute(query.limit(1000)).scalars().all()


@router.get("/items/{content_id}", response_model=TourItemDetail)
def get_tour_item(content_id: str, db: Session = Depends(get_db)):
    item = db.execute(
        select(TourItem).where(TourItem.content_id == content_id)
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="해당 콘텐츠를 찾을 수 없습니다.")
    return item
