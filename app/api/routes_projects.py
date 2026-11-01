from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])

@router.get("/")
async def list_projects():
    return {"projects": []}
