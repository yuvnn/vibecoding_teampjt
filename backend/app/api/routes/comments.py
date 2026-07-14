from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.comment import Comment
from app.models.post import Post
from app.schemas.comment import CommentCreate, CommentOut
from app.schemas.post import PasswordCheck

router = APIRouter(tags=["comments"])


@router.get("/api/posts/{post_id}/comments", response_model=list[CommentOut])
def list_comments(post_id: int, db: Session = Depends(get_db)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return (
        db.execute(
            select(Comment).where(Comment.post_id == post_id).order_by(Comment.created_at)
        )
        .scalars()
        .all()
    )


@router.post("/api/posts/{post_id}/comments", response_model=CommentOut, status_code=201)
def create_comment(post_id: int, payload: CommentCreate, db: Session = Depends(get_db)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    comment = Comment(post_id=post_id, content=payload.content, password=payload.password)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/api/comments/{comment_id}")
def delete_comment(comment_id: int, payload: PasswordCheck, db: Session = Depends(get_db)):
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    if comment.password != payload.password:
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")
    db.delete(comment)
    db.commit()
    return {"detail": "댓글이 삭제되었습니다."}
