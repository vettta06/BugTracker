from app.database import get_db
from app.logger import logger
from app.models import Bug, Comment, User
from app.schemas import CommentCreate, CommentRead
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/", response_model=CommentRead, status_code=201)
def create_comment(
    comment: CommentCreate, db: Session = Depends(get_db)
) -> CommentRead:
    bug = db.query(Bug).filter(Bug.id == comment.bug_id).first()
    if not bug:
        logger.warning(
            "comment_creation_failed",
            reason="bug_not_found",
        )
        raise HTTPException(status_code=404, detail="Bug not found")

    user = db.query(User).filter(User.id == comment.author_id).first()
    if not user:
        logger.warning(
            "comment_creation_failed",
            reason="user_not_found",
            author_id=comment.author_id,
        )
        raise HTTPException(status_code=404, detail="User not found")

    db_comment = Comment(**comment.model_dump())
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    logger.info(
        "comment_created",
        comment_id=db_comment.id,
        bug_id=db_comment.bug_id,
        author_id=db_comment.author_id,
    )
    return db_comment


@router.get("/", response_model=list[CommentRead])
def get_comments(db: Session = Depends(get_db)):
    comments = db.query(Comment).all()
    logger.debug("comments_listed", count=len(comments))
    return comments


@router.get("/{comment_id}", response_model=CommentRead)
def get_comment(comment_id: int, db: Session = Depends(get_db)) -> CommentRead:
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not db_comment:
        logger.warning("comment_not_found", comment_id=comment_id)
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment


@router.put("/{comment_id}", response_model=CommentRead)
def update_comment(
    comment_id: int, comment: CommentCreate, db: Session = Depends(get_db)
) -> CommentRead:
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not db_comment:
        logger.warning(
            "comment_update_failed", reason="comment_not_found", comment_id=comment_id
        )
        raise HTTPException(status_code=404, detail="Comment not found")

    bug = db.query(Bug).filter(Bug.id == comment.bug_id).first()
    if not bug:
        logger.warning(
            "comment_update_failed",
            reason="bug_not_found",
            bug_id=comment.bug_id,
        )
        raise HTTPException(status_code=404, detail="Bug not found")

    user = db.query(User).filter(User.id == comment.author_id).first()
    if not user:
        logger.warning(
            "comment_update_failed",
            reason="user_not_found",
            author_id=comment.author_id,
        )
        raise HTTPException(status_code=404, detail="User not found")

    db_comment.text = comment.text
    db_comment.bug_id = comment.bug_id
    db_comment.author_id = comment.author_id

    db.commit()
    db.refresh(db_comment)
    logger.info("comment_updated", comment_id=db_comment.id)
    return db_comment


@router.delete("/{comment_id}", status_code=204)
def delete_comment(comment_id: int, db: Session = Depends(get_db)) -> None:
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not db_comment:
        logger.warning(
            "comment_deletion_failed", reason="comment_not_found", comment_id=comment_id
        )
        raise HTTPException(status_code=404, detail="Comment not found")
    db.delete(db_comment)
    db.commit()
    logger.info("comment_deleted", comment_id=comment_id)
