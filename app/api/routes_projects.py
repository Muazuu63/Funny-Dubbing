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


from pydantic import BaseModel, Field

class GeneratePreviewRequest(BaseModel):
    project_id: str
    input_video_path: str
    target_language: str = "Bangla"
    comedy_profile: Optional[str] = None


@router.post("/upload")
async def upload_project_video(file: UploadFile = File(...)):
    """Uploads a source video to temp/uploads and returns the local file path with duration."""
    upload_dir = settings.TEMP_DIR / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    clean_name = f"{uuid.uuid4().hex[:8]}_{Path(file.filename or 'video.mp4').name}"
    target_path = upload_dir / clean_name

    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    size_mb = round(target_path.stat().st_size / (1024 * 1024), 2)
    duration_sec = 0.0

    try:
        import cv2
        cap = cv2.VideoCapture(str(target_path))
        if cap.isOpened():
            fps = float(cap.get(cv2.CAP_PROP_FPS) or 25.0)
            frames = float(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
            if fps > 0 and frames > 0:
                duration_sec = round(frames / fps, 2)
            cap.release()
    except Exception:
        pass

    minutes = int(duration_sec) // 60
    seconds = int(duration_sec) % 60
    formatted_duration = f"{minutes:02d}:{seconds:02d}"

    return {
        "status": "success",
        "filename": file.filename,
        "saved_path": str(target_path).replace("\\", "/"),
        "size_mb": size_mb,
        "duration_sec": duration_sec,
        "formatted_duration": formatted_duration,
    }


@router.post("/generate-preview")
async def generate_project_preview(payload: GeneratePreviewRequest):
    """
    Analyzes the uploaded video's actual duration and creates a full-length,
    timeline-synchronized comedic script and voice preview covering every second.
    """
    video_path = Path(payload.input_video_path)
    duration_sec = 30.0

    if video_path.exists():
        try:
            import cv2
            cap = cv2.VideoCapture(str(video_path))
            if cap.isOpened():
                fps = float(cap.get(cv2.CAP_PROP_FPS) or 25.0)
                frames = float(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
                if fps > 0 and frames > 0:
                    duration_sec = round(frames / fps, 2)
                cap.release()
        except Exception:
            pass

    from app.providers.gemini_provider import LocalScriptEngine
    from app.api.routes_approval import get_project_approval_state, set_project_approval_state

    script_data = LocalScriptEngine.generate_full_length_script(
        duration_sec=duration_sec,
        target_language=payload.target_language,
        comedy_profile=payload.comedy_profile
    )

    approval_state = get_project_approval_state(payload.project_id)
    approval_state.status = "WAITING_FOR_VOICE_APPROVAL"
    approval_state.script_text = script_data["full_script_text"]
    approval_state.duration_sec = script_data["duration_sec"]
    approval_state.formatted_duration = script_data["formatted_duration"]
    approval_state.notes = f"Full length comedy script ({script_data['formatted_duration']}, {script_data['total_words']} words, {script_data['total_scenes']} scenes)"
    set_project_approval_state(payload.project_id, approval_state)

    return {
        "status": "success",
        "project_id": payload.project_id,
        "duration_sec": script_data["duration_sec"],
        "formatted_duration": script_data["formatted_duration"],
        "script_text": script_data["full_script_text"],
        "total_words": script_data["total_words"],
        "scenes": script_data["scenes"],
        "approval_state": approval_state.model_dump()
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
