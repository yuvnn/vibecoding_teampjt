from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.category import Category
from app.models.post import Post
from app.schemas.post import (
    PasswordCheck,
    PostCreate,
    PostDetailOut,
    PostListResponse,
    PostOut,
    PostUpdate,
)

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.get("", response_model=PostListResponse)
def list_posts(
    category_id: int | None = None,
    keyword: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = select(Post)
    if category_id is not None:
        query = query.where(Post.category_id == category_id)
    if keyword:
        like = f"%{keyword}%"
        query = query.where(or_(Post.title.ilike(like), Post.content.ilike(like)))

    total_count = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    posts = (
        db.execute(query.order_by(Post.id.desc()).offset((page - 1) * limit).limit(limit))
        .scalars()
        .all()
    )
    return PostListResponse(total_count=total_count, page=page, limit=limit, posts=posts)


@router.post("", response_model=PostOut, status_code=201)
def create_post(payload: PostCreate, db: Session = Depends(get_db)):
    category = db.get(Category, payload.category_id)
    if not category:
        raise HTTPException(status_code=422, detail="존재하지 않는 카테고리입니다.")
    post = Post(**payload.model_dump())
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.get("/{post_id}", response_model=PostDetailOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    post.view_count += 1
    db.commit()
    db.refresh(post)
    return PostDetailOut(
        id=post.id,
        category_id=post.category_id,
        category_name=post.category.name,
        title=post.title,
        content=post.content,
        view_count=post.view_count,
        created_at=post.created_at,
    )


@router.put("/{post_id}", response_model=PostOut)
def update_post(post_id: int, payload: PostUpdate, db: Session = Depends(get_db)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    if post.password != payload.password:
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")
    post.title = payload.title
    post.content = payload.content
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
