"""
Projects API Router for AI-VPS.
Master Architecture v2.2 & PRD v2.2 Aligned.

Endpoints:
- GET /api/v1/projects: List all projects.
- POST /api/v1/projects: Create new project with default mixer state.
- GET /api/v1/projects/{project_id}: Get project details, manifests & mixer telemetry.
- DELETE /api/v1/projects/{project_id}: Cascade delete project.
- POST /api/v1/projects/{project_id}/resume: Reconcile and resume interrupted project.
"""
import shutil
import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pathlib import Path

from app.db.database import get_db
from app.db import crud
from app.db.models import Project, ProjectCreate
from app.core.reconciliation import ReconciliationEngine
from app.config import settings

router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])


@router.get("", response_model=List[Project])
@router.get("/", response_model=List[Project])
async def list_projects():
    """Lists all user projects in reverse chronological order."""
    async with get_db(critical=False) as db:
        await crud.init_db(db)
        return await crud.list_projects(db)


@router.post("", response_model=Project)
@router.post("/", response_model=Project)
async def create_project(payload: ProjectCreate):
    """Creates a new project and initializes its default AudioMixerState."""
    async with get_db(critical=True) as db:
        await crud.init_db(db)
        created = await crud.create_project(db, payload)
        # Ensure project directory exists
        proj_dir = settings.PROJECTS_DIR / created.id
        proj_dir.mkdir(parents=True, exist_ok=True)
        return created


@router.post("/upload")
async def upload_project_video(file: UploadFile = File(...)):
    """Uploads a source video to temp/uploads and returns the local file path."""
    upload_dir = settings.TEMP_DIR / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    clean_name = f"{uuid.uuid4().hex[:8]}_{Path(file.filename or 'video.mp4').name}"
    target_path = upload_dir / clean_name

    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    size_mb = round(target_path.stat().st_size / (1024 * 1024), 2)
    return {
        "status": "success",
        "filename": file.filename,
        "saved_path": str(target_path).replace("\\", "/"),
        "size_mb": size_mb,
    }


@router.get("/{project_id}")
async def get_project_details(project_id: str):
    """Retrieves project details, step checkpoints, and audio mixer states."""
    async with get_db(critical=False) as db:
        await crud.init_db(db)
        project = await crud.get_project(db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")

        mixer = await crud.get_mixer_state(db, project_id)
        manifests = await crud.list_manifests_by_project(db, project_id)

        return {
            "project": project,
            "mixer_state": mixer,
            "manifests": manifests,
        }


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """Cascade deletes project and its associated metadata."""
    async with get_db(critical=True) as db:
        await crud.init_db(db)
        deleted = await crud.delete_project(db, project_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")
        
        # Clean local folder if exists
        proj_dir = settings.PROJECTS_DIR / project_id
        if proj_dir.exists():
            import shutil
            shutil.rmtree(proj_dir, ignore_errors=True)

        return {"status": "ok", "deleted": project_id}


@router.post("/{project_id}/resume")
async def resume_project_checkpoints(project_id: str):
    """Idempotently reconciles task checkpoints and resumes interrupted processing."""
    proj_dir = settings.PROJECTS_DIR / project_id
    if not proj_dir.exists():
        raise HTTPException(status_code=404, detail=f"Project storage directory not found: {project_id}")

    reconciler = ReconciliationEngine(proj_dir)
    async with get_db(critical=True) as db:
        await crud.init_db(db)
        manifests = await crud.list_manifests_by_project(db, project_id)
        results = []
        for m in manifests:
            res = await reconciler.reconcile_single_task(m.task_id, db)
            results.append(res)

        return {
            "project_id": project_id,
            "reconciled_tasks": results,
            "status": "RESUMED",
        }
