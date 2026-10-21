from app.database import get_db
from app.logger import logger
from app.metrics import PROJECTS_CREATED
from app.models import Project
from app.schemas import ProjectCreate, ProjectRead
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectRead, status_code=201)
def create_project(
    project: ProjectCreate, db: Session = Depends(get_db)
) -> ProjectRead:
    db_project = Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    logger.info(
        "project_created", project_id=db_project.id, project_name=db_project.name
    )
    PROJECTS_CREATED.inc()
    return db_project


@router.get("/", response_model=list[ProjectRead])
def get_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    logger.debug("projects_listed", count=len(projects))
    return projects


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)) -> ProjectRead:
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        logger.warning("project_not_found", project_id=project_id)
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project


@router.put("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int, project: ProjectCreate, db: Session = Depends(get_db)
) -> ProjectRead:
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        logger.warning(
            "project_update_failed", reason="project_not_found", project_id=project_id
        )
        raise HTTPException(status_code=404, detail="Project not found")
    db_project.name = project.name
    db_project.description = project.description
    db.commit()
    db.refresh(db_project)
    logger.info("project_updated", project_id=db_project.id)
    return db_project


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)) -> None:
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        logger.warning(
            "project_deletion_failed", reason="project_not_found", project_id=project_id
        )
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(db_project)
    db.commit()
    logger.info("project_deleted", project_id=project_id)
