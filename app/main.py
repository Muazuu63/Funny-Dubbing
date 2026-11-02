"""
AI-VPS Master FastAPI Application Entrypoint.
Master Architecture v2.2 & PRD v2.2 Aligned.

Single-Port Runtime Architecture:
Strictly bound to http://127.0.0.1:8000
No fallback runtime ports.

Security & Integrity:
- Host Header Guard (DNS Rebinding prevention)
- Strict Origin Validation (Wildcard CORS forbidden)
- Permanent Zero Extra Cost Hard-Lock
- Startup Reconciliation Engine (Cases A to K)
- Built Frontend Single-Port Serving (/ serving frontend/dist)
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.core.security import (
    HostHeaderValidationMiddleware,
    StrictOriginMiddleware,
    ZeroCostHardLockMiddleware,
)
from app.core.reconciliation import reconcile_tasks_on_startup
from app.db.database import get_db
from app.db import crud

# Import all API Routers
from app.api.routes_projects import router as projects_router
from app.api.routes_modes import router as modes_router
from app.api.routes_approval import router as approval_router
from app.api.routes_settings import router as settings_router
from app.api.routes_training import router as training_router
from app.api.websocket import router as websocket_router

logger = logging.getLogger("ai_vps.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle management:
    1. Ensures storage and workspace directories exist.
    2. Initializes SQLite tables and schemas.
    3. Runs crash reconciliation for all pending/interrupted tasks.
    """
    settings.ensure_directories()
    try:
        async with get_db(critical=True) as db:
            await crud.init_db(db)
        reconcile_res = await reconcile_tasks_on_startup()
        logger.info(f"Startup reconciliation complete: {reconcile_res}")
    except Exception as e:
        logger.error(f"Startup initialization error: {e}", exc_info=True)

    yield

    logger.info("AI-VPS Studio shutting down cleanly.")


app = FastAPI(
    title="AI-VPS Studio Backend",
    version="2.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# -------------------------------------------------------------
# Security Middlewares (Strict single-port localhost security)
# -------------------------------------------------------------
app.add_middleware(ZeroCostHardLockMiddleware)
app.add_middleware(StrictOriginMiddleware)
app.add_middleware(HostHeaderValidationMiddleware)


# -------------------------------------------------------------
# Global Exception Handler
# -------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": str(exc),
            "path": request.url.path,
        }
    )


# -------------------------------------------------------------
# API Router Registration
# -------------------------------------------------------------
app.include_router(projects_router)
app.include_router(modes_router)
app.include_router(approval_router)
app.include_router(settings_router)
app.include_router(training_router)
app.include_router(websocket_router)


# -------------------------------------------------------------
# Health and Info Endpoints
# -------------------------------------------------------------
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint used by dashboard and desktop shell."""
    return {
        "status": "HEALTHY",
        "service": "AI-VPS Studio",
        "version": "2.2.0",
        "host": settings.HOST,
        "port": settings.PORT,
        "offline_mode": settings.OFFLINE_MODE_ENABLED,
    }


# -------------------------------------------------------------
# Built Frontend Static File Serving (/ serving frontend/dist)
# -------------------------------------------------------------
if settings.FRONTEND_DIST_DIR.exists() and (settings.FRONTEND_DIST_DIR / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(settings.FRONTEND_DIST_DIR), html=True), name="frontend")
else:
    @app.get("/")
    async def root_info():
        return {
            "name": "AI-VPS Studio API",
            "version": "2.2.0",
            "dashboard_url": f"http://{settings.HOST}:{settings.PORT}",
            "docs": f"http://{settings.HOST}:{settings.PORT}/docs",
            "status": "READY",
        }
