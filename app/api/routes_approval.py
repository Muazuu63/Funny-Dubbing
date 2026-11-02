"""
Universal Voice Approval Gateway API Routes.
Master Architecture v2.2 & PRD v2.2 Aligned.

Enforces:
1. Unified Voice Approval Policy:
   Whether AI Voice or Real Voice, final video export is strictly blocked
   until user previews the synthesized voice and explicitly approves.
2. Supports actions: APPROVE, REJECT, REGENERATE.
"""
from enum import Enum
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/approval", tags=["Voice Approval Gateway"])


class ApprovalAction(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REGENERATE = "REGENERATE"


class ApprovalRequest(BaseModel):
    action: ApprovalAction
    notes: Optional[str] = None
    edited_dialogue: Optional[str] = None


class ApprovalState(BaseModel):
    project_id: str
    status: str = "WAITING_FOR_VOICE_APPROVAL"  # WAITING_FOR_VOICE_APPROVAL, APPROVED, REJECTED, REGENERATION_REQUESTED
    audio_preview_url: Optional[str] = None
    notes: Optional[str] = None
    script_text: Optional[str] = None
    translation_script_text: Optional[str] = None
    commentary_script_text: Optional[str] = None
    has_original_voice: Optional[bool] = False
    duration_sec: Optional[float] = None
    formatted_duration: Optional[str] = None
    approved_at: Optional[str] = None


class RegenerateRequest(BaseModel):
    notes: Optional[str] = None
    edited_script: Optional[str] = None


# In-memory approval tracker (also integrated with task manifests)
_approval_store: Dict[str, ApprovalState] = {}


def get_project_approval_state(project_id: str) -> ApprovalState:
    if project_id not in _approval_store:
        _approval_store[project_id] = ApprovalState(project_id=project_id)
    return _approval_store[project_id]


def set_project_approval_state(project_id: str, state: ApprovalState) -> None:
    _approval_store[project_id] = state


@router.get("/status/{project_id}", response_model=ApprovalState)
async def get_approval_status(project_id: str):
    return get_project_approval_state(project_id)


@router.post("/voice/{project_id}", response_model=ApprovalState)
async def submit_voice_approval(project_id: str, payload: ApprovalRequest):
    state = get_project_approval_state(project_id)
    import datetime

    if payload.action == ApprovalAction.APPROVE:
        state.status = "APPROVED"
        state.approved_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        state.notes = payload.notes
    elif payload.action == ApprovalAction.REJECT:
        state.status = "REJECTED"
        state.notes = payload.notes
    elif payload.action == ApprovalAction.REGENERATE:
        state.status = "REGENERATION_REQUESTED"
        state.notes = payload.notes

    set_project_approval_state(project_id, state)
    return state


@router.post("/{project_id}/approve", response_model=ApprovalState)
async def approve_project_voice(project_id: str):
    import datetime
    state = get_project_approval_state(project_id)
    state.status = "APPROVED"
    state.approved_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    set_project_approval_state(project_id, state)
    return state


@router.post("/{project_id}/regenerate", response_model=ApprovalState)
async def regenerate_project_voice(project_id: str, payload: RegenerateRequest):
    state = get_project_approval_state(project_id)
    state.status = "REGENERATION_REQUESTED"
    state.notes = payload.notes
    if payload.edited_script:
        state.script_text = payload.edited_script
    set_project_approval_state(project_id, state)
    return state


@router.post("/{project_id}/reject", response_model=ApprovalState)
async def reject_project_voice(project_id: str, payload: RegenerateRequest):
    state = get_project_approval_state(project_id)
    state.status = "REJECTED"
    state.notes = payload.notes
    set_project_approval_state(project_id, state)
    return state
