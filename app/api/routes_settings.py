"""Settings API router for AI-VPS."""
from fastapi import APIRouter

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("/")
async def get_settings():
    return {"status": "ok", "settings": {}}
