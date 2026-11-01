from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/modes", tags=["Production Modes"])

@router.get("/")
async def list_modes():
    return {
        "modes": [
            {"id": "mode_01", "name": "Funny Video Dubbing Studio", "status": "ACTIVE", "phase": "P1"},
            {"id": "mode_02", "name": "Cartoon Video Re-Creation Studio", "status": "ACTIVE", "phase": "P1"},
            {"id": "mode_03", "name": "AI Autonomous Content Creator", "status": "ACTIVE", "phase": "P1"},
            {"id": "mode_04", "name": "AI Video Enhancement Studio", "status": "PLANNED", "phase": "P2"},
            {"id": "mode_05", "name": "AI Voice Studio", "status": "PLANNED", "phase": "P2"},
            {"id": "mode_06", "name": "AI Subtitle & Translation Studio", "status": "PLANNED", "phase": "P2"},
            {"id": "mode_07", "name": "AI Shorts & Reels Creator", "status": "PLANNED", "phase": "P3"},
            {"id": "mode_08", "name": "AI Video Editor Studio", "status": "PLANNED", "phase": "P3"},
            {"id": "mode_09", "name": "AI Thumbnail Creator", "status": "PLANNED", "phase": "P3"},
            {"id": "mode_10", "name": "AI Background & Object Studio", "status": "FUTURE", "phase": "P4"},
            {"id": "mode_11", "name": "AI Music & Sound Studio", "status": "FUTURE", "phase": "P4"}
        ]
    }
