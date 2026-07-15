from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_db
from app.models.category import Category
from app.models.post import Post
from app.models.post_category import PostCategory
from app.models.post_place import PostPlace
from app.schemas.post import (
    PasswordCheck,
    PostCreate,
    PostDetailOut,
    PostListResponse,
    PostOut,
    PostUpdate,
)

router = APIRouter(prefix="/api/posts", tags=["posts"])

_LIST_LOAD_OPTIONS = (selectinload(Post.post_categories), selectinload(Post.post_places))
_DETAIL_LOAD_OPTIONS = (
    selectinload(Post.post_categories).selectinload(PostCategory.category),
    selectinload(Post.post_places),
)

# Posts have no geo column of their own — a post "belongs" to a header
# region if one of its attached places' addresses mentions a province that
# region covers. Matches the data/raw/<region> folder names (= tour_masters
# .region values) so this stays consistent with the map's own region split.
REGION_PROVINCE_KEYWORDS: dict[str, list[str]] = {
    "대전_충청권": ["대전", "충청남도", "충청북도", "세종"],
    "서울": ["서울"],
    "구미_경북권": ["경상북도", "대구"],
    "광주_전라권": ["광주", "전라남도", "전라북도", "전북특별자치도"],
    "부산": ["부산", "울산", "경상남도"],
}


@router.get("", response_model=PostListResponse)
def list_posts(
    category_id: int | None = None,
    region: str | None = None,
    keyword: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = select(Post).options(*_LIST_LOAD_OPTIONS)
    if category_id is not None:
        query = query.where(Post.post_categories.any(PostCategory.category_id == category_id))
    if keyword:
        like = f"%{keyword}%"
        query = query.where(or_(Post.title.ilike(like), Post.content.ilike(like)))
    keywords = REGION_PROVINCE_KEYWORDS.get(region or "")
    if keywords:
        # A post with no attached place at all has no way to prove it
        # belongs to a *different* region, so it stays visible everywhere
        # rather than disappearing the moment any region filter is applied.
        province_match = or_(*(PostPlace.address.ilike(f"%{kw}%") for kw in keywords))
        query = query.where(or_(~Post.post_places.any(), Post.post_places.any(province_match)))

    total_count = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    posts = (
        db.execute(query.order_by(Post.id.desc()).offset((page - 1) * limit).limit(limit))
        .unique()
        .scalars()
        .all()
    )
    return PostListResponse(total_count=total_count, page=page, limit=limit, posts=posts)


@router.post("", response_model=PostOut, status_code=201)
def create_post(payload: PostCreate, db: Session = Depends(get_db)):
    categories = db.execute(select(Category).where(Category.id.in_(payload.category_ids))).scalars().all()
    if len(categories) != len(payload.category_ids):
        raise HTTPException(status_code=422, detail="존재하지 않는 카테고리가 포함되어 있습니다.")

    first_place = payload.places[0] if payload.places else None
    post = Post(
        category_id=payload.category_ids[0],
        title=payload.title,
        content=payload.content,
        password=payload.password,
        place_name=first_place.place_name if first_place else None,
        address=first_place.address if first_place else None,
        map_x=first_place.map_x if first_place else None,
        map_y=first_place.map_y if first_place else None,
    )
    post.post_categories = [PostCategory(category_id=cid) for cid in payload.category_ids]
    post.post_places = [PostPlace(**place.model_dump()) for place in payload.places]
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.get("/{post_id}", response_model=PostDetailOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.execute(
        select(Post).options(*_DETAIL_LOAD_OPTIONS).where(Post.id == post_id)
    ).unique().scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    post.view_count += 1
    db.commit()
    db.refresh(post)
    return post


@router.put("/{post_id}", response_model=PostOut)
def update_post(post_id: int, payload: PostUpdate, db: Session = Depends(get_db)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    if post.password != payload.password:
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")

    categories = db.execute(select(Category).where(Category.id.in_(payload.category_ids))).scalars().all()
    if len(categories) != len(payload.category_ids):
        raise HTTPException(status_code=422, detail="존재하지 않는 카테고리가 포함되어 있습니다.")

    post.title = payload.title
    post.content = payload.content
    post.category_id = payload.category_ids[0]
    post.post_categories = [PostCategory(category_id=cid) for cid in payload.category_ids]

    first_place = payload.places[0] if payload.places else None
    post.place_name = first_place.place_name if first_place else None
    post.address = first_place.address if first_place else None
    post.map_x = first_place.map_x if first_place else None
    post.map_y = first_place.map_y if first_place else None
    post.post_places = [PostPlace(**place.model_dump()) for place in payload.places]

    db.commit()
    db.refresh(post)
    return post


@router.delete("/{post_id}")
def delete_post(post_id: int, payload: PasswordCheck, db: Session = Depends(get_db)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    if post.password != payload.password:
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")
    db.delete(post)
    db.commit()
    return {"detail": "게시글이 성공적으로 삭제되었습니다."}
