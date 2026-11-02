"""
Training Center & Reusable Asset Hub API Router.
Master Architecture v2.2 & PRD v2.2 Aligned.

Exposes REST endpoints for:
1. Managing comedy style profiles, voice presets, character sheets, and punchline timing.
2. AI-assisted reference analysis without GPU training overhead.
"""
import shutil
import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel

from app.config import settings
from app.core.training_center import (
    training_center,
    TrainingProfile,
    TrainingProfileCategory,
)

router = APIRouter(prefix="/api/v1/training", tags=["Shared Training Center Hub"])


class CreateProfileRequest(BaseModel):
    name: str
    category: TrainingProfileCategory
    description: Optional[str] = None
    parameters: Dict[str, Any] = {}
    reference_media_path: Optional[str] = None


class ReferenceAnalysisRequest(BaseModel):
    video_path: str


@router.get("/profiles", response_model=List[TrainingProfile])
async def list_profiles(category: Optional[TrainingProfileCategory] = Query(None)):
    """Lists reusable training profiles (comedy styles, dialogue patterns, voice profiles)."""
    return training_center.list_profiles(category=category)


@router.post("/profiles", response_model=TrainingProfile)
async def create_profile(payload: CreateProfileRequest):
    """Saves a new reusable profile for use across Mode 01, 02, and 03."""
    profile = TrainingProfile(
        name=payload.name,
        category=payload.category,
        description=payload.description,
        parameters=payload.parameters,
        reference_media_path=payload.reference_media_path,
    )
    return training_center.save_profile(profile)


@router.get("/profiles/{profile_id}", response_model=TrainingProfile)
async def get_profile(profile_id: str):
    """Retrieves a specific training profile by ID."""
    profile = training_center.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile '{profile_id}' not found.")
    return profile


@router.delete("/profiles/{profile_id}")
async def delete_profile(profile_id: str):
    """Deletes a training profile."""
    success = training_center.delete_profile(profile_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Profile '{profile_id}' not found.")
    return {"status": "ok", "deleted": profile_id}


@router.post("/analyze-reference")
async def analyze_reference(payload: ReferenceAnalysisRequest):
    """
    Analyzes reference video to extract comic cadence and pacing heuristics.
    No GPU backpropagation or model retraining.
    """
    path = Path(payload.video_path)
    try:
        analysis = training_center.analyze_reference_video(path)
        return {"status": "ok", "analysis": analysis}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Reference video not found: {payload.video_path}")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.get("/ledger")
async def get_learning_ledger():
    """Returns all historical learning records and cumulative improvement timeline."""
    records = training_center.get_learning_ledger()
    return {"total_records": len(records), "records": [r.model_dump() for r in records]}


@router.get("/ledger/{record_id}")
async def get_learning_record(record_id: str):
    """Retrieves full learning record with markdown document."""
    records = training_center.get_learning_ledger()
    for r in records:
        if r.record_id == record_id:
            return r.model_dump()
    raise HTTPException(status_code=404, detail="Learning record not found")


@router.get("/export-ledger")
async def export_learning_ledger():
    """Exports and downloads the complete AI knowledge ledger JSON for backup."""
    ledger_path = training_center.ledger_file
    if not ledger_path.exists():
        raise HTTPException(status_code=404, detail="No learning ledger found yet.")
    return FileResponse(
        path=str(ledger_path),
        media_type="application/json",
        filename="muazu_learning_ledger_backup.json"
    )


@router.post("/upload-reference")
async def upload_training_reference(file: UploadFile = File(...)):
    """Uploads comedy reference video to data/training_references for AI analysis."""
    ref_dir = settings.DATA_DIR / "training_references"
    ref_dir.mkdir(parents=True, exist_ok=True)

    clean_name = f"{uuid.uuid4().hex[:8]}_{Path(file.filename or 'reference.mp4').name}"
    target_path = ref_dir / clean_name

    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    size_mb = round(target_path.stat().st_size / (1024 * 1024), 2)
    return {
        "status": "success",
        "filename": file.filename,
        "saved_path": str(target_path).replace("\\", "/"),
        "size_mb": size_mb,
    }
