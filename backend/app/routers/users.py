from app.database import get_db
from app.logger import logger
from app.models import User
from app.schemas import UserCreate, UserRead
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info("user_created", user_id=db_user.id)
    return db_user


@router.get("/", response_model=list[UserRead])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    logger.debug("users_listed", count=len(users))
    return users


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)) -> UserRead:
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        logger.warning("user_not_found", user_id=user_id)
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int, user: UserCreate, db: Session = Depends(get_db)
) -> UserRead:
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        logger.warning("user_update_failed", reason="user_not_found", user_id=user_id)
        raise HTTPException(status_code=404, detail="User not found")
    db_user.name = user.name
    db_user.email = user.email
    db.commit()
    db.refresh(db_user)
    logger.info("user_updated", user_id=user_id)
    return db_user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)) -> None:
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        logger.warning("user_deletion_failed", reason="user_not_found", user_id=user_id)
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    logger.info("user_deleted", user_id=user_id)
