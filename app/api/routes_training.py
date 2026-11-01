"""Training & Voice Profile API router for AI-VPS."""
from fastapi import APIRouter

router = APIRouter(prefix="/training", tags=["training"])

@router.get("/profiles")
async def list_profiles():
    return {"status": "ok", "profiles": []}
