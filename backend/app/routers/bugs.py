from app.database import get_db
from app.logger import logger
from app.models import Bug, Project, User
from app.schemas import BugCreate, BugRead
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/bugs", tags=["bugs"])


@router.post("/", response_model=BugRead, status_code=201)
def create_bug(bug: BugCreate, db: Session = Depends(get_db)) -> BugRead:
    project = db.query(Project).filter(Project.id == bug.project_id).first()
    if not project:
        logger.warning(
            "bug_creation_failed", reason="project_not_found", project_id=bug.project_id
        )
        raise HTTPException(status_code=404, detail="Project not found")
    if bug.assignee_id:
        user = db.query(User).filter(User.id == bug.assignee_id).first()
        if not user:
            logger.warning(
                "bug_creation_failed",
                reason="assignee_not_found",
                assignee_id=bug.assignee_id,
            )
            raise HTTPException(status_code=404, detail="Assignee not found")
    db_bug = Bug(**bug.model_dump())
    db.add(db_bug)
    db.commit()
    db.refresh(db_bug)
    logger.info("bug_created", bug_id=db_bug.id)
    return db_bug


@router.get("/", response_model=list[BugRead])
def get_bugs(db: Session = Depends(get_db)):
    bugs = db.query(Bug).all()
    logger.debug("bugs_listed", count=len(bugs))
    return bugs


@router.get("/{bug_id}", response_model=BugRead)
def get_bug(bug_id: int, db: Session = Depends(get_db)) -> BugRead:
    db_bug = db.query(Bug).filter(Bug.id == bug_id).first()
    if not db_bug:
        logger.warning("bug_not_found", bug_id=bug_id)
        raise HTTPException(status_code=404, detail="Bug not found")
    return db_bug


@router.put("/{bug_id}", response_model=BugRead)
def update_bug(bug_id: int, bug: BugCreate, db: Session = Depends(get_db)) -> BugRead:
    db_bug = db.query(Bug).filter(Bug.id == bug_id).first()
    if not db_bug:
        logger.warning("bug_update_failed", reason="bug_not_found", bug_id=bug_id)
        raise HTTPException(status_code=404, detail="Bug not found")

    project = db.query(Project).filter(Project.id == bug.project_id).first()
    if not project:
        logger.warning(
            "bug_update_failed", reason="project_not_found", project_id=bug.project_id
        )
        raise HTTPException(status_code=404, detail="Project not found")

    if bug.assignee_id:
        user = db.query(User).filter(User.id == bug.assignee_id).first()
        if not user:
            logger.warning(
                "bug_update_failed",
                reason="assignee_not_found",
                assignee_id=bug.assignee_id,
            )
            raise HTTPException(status_code=404, detail="Assignee not found")

    db_bug.title = bug.title
    db_bug.description = bug.description
    db_bug.status = bug.status
    db_bug.priority = bug.priority
    db_bug.project_id = bug.project_id
    db_bug.assignee_id = bug.assignee_id

    db.commit()
    db.refresh(db_bug)
    logger.info("bug_updated", bug_id=db_bug.id)
    return db_bug


@router.delete("/{bug_id}", status_code=204)
def delete_bug(bug_id: int, db: Session = Depends(get_db)) -> None:
    db_bug = db.query(Bug).filter(Bug.id == bug_id).first()
    if not db_bug:
        logger.warning("bug_deletion_failed", reason="bug_not_found", bug_id=bug_id)
        raise HTTPException(status_code=404, detail="Bug not found")
    db.delete(db_bug)
    db.commit()
    logger.info("bug_deleted", bug_id=bug_id)
