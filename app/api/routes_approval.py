from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/approval", tags=["Voice Approval"])

@router.get("/status/{project_id}")
async def get_approval_status(project_id: str):
    return {
        "project_id": project_id,
        "status": "WAITING_FOR_APPROVAL",
        "primary_language": "Bangla",
        "preview_audio_url": None
    }
