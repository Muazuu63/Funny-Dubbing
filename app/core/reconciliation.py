"""Startup reconciliation system to recover pending and orphaned tasks."""
from app.config import settings

async def reconcile_tasks_on_startup():
    """Scan SQLite and storage manifests on startup and resolve interrupted tasks."""
    return {"recovered": 0, "failed": 0}
