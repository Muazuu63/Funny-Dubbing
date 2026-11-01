"""
AI-VPS Main FastAPI Application Entrypoint.
Binds strictly to http://127.0.0.1:8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(
    title="AI-VPS Studio Backend",
    version="2.2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware (Strict Origins Only - Wildcard Forbidden)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.TRUSTED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint used by frontend and desktop shell."""
    return {
        "status": "HEALTHY",
        "service": "AI-VPS Studio",
        "version": "2.2.0",
        "host": settings.HOST,
        "port": settings.PORT,
        "offline_mode": settings.OFFLINE_MODE_ENABLED
    }
