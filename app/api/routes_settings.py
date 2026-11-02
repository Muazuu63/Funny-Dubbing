"""
Settings API Router for AI-VPS.
Master Architecture v2.2 & PRD v2.2 Aligned.

Features:
1. Lists verified free AI models and offline mode flags.
2. Secure API Key Management via Windows Credential Manager.
3. Plaintext keys are NEVER exposed (returns sha256 fingerprint & masked string).
4. Real-time host RAM & VRAM metrics via MemoryManager.
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.core.security import (
    store_secure_credential,
    retrieve_secure_credential,
    compute_key_fingerprint,
    mask_api_key,
)
from app.core.memory_manager import memory_manager
from app.providers.gemini_provider import OFFICIAL_FREE_TIER_MODELS

router = APIRouter(prefix="/api/v1/settings", tags=["Settings & Key Management"])


class GeminiKeyRequest(BaseModel):
    api_key: str


class OfflineModeToggleRequest(BaseModel):
    enabled: bool


@router.get("")
@router.get("/")
async def get_system_settings():
    """Returns verified free models, active model, offline status, and RAM telemetry."""
    stored_key = retrieve_secure_credential("gemini") or ""
    return {
        "active_gemini_model": "gemini-1.5-flash",
        "verified_free_models": sorted(list(OFFICIAL_FREE_TIER_MODELS)),
        "offline_mode_enabled": settings.OFFLINE_MODE_ENABLED,
        "single_port_binding": f"{settings.HOST}:{settings.PORT}",
        "api_key_configured": bool(stored_key.strip()),
        "api_key_fingerprint": compute_key_fingerprint(stored_key),
        "api_key_masked": mask_api_key(stored_key),
        "system_memory": memory_manager.get_system_memory(),
    }


@router.post("/gemini-key")
async def save_gemini_api_key(payload: GeminiKeyRequest):
    """
    Saves Gemini API key securely in OS-level Windows Credential Manager.
    Returns SHA-256 fingerprint and masked string. Plaintext key is NOT returned.
    """
    key = payload.api_key.strip()
    if not key:
        raise HTTPException(status_code=400, detail="API key cannot be empty.")

    store_secure_credential("gemini", key)
    return {
        "status": "SAVED_SECURELY",
        "storage": "Windows Credential Manager",
        "api_key_fingerprint": compute_key_fingerprint(key),
        "api_key_masked": mask_api_key(key),
    }


@router.post("/offline-mode")
async def toggle_offline_mode(payload: OfflineModeToggleRequest):
    """Toggles offline mode lock. When enabled, all external cloud calls are blocked."""
    settings.OFFLINE_MODE_ENABLED = payload.enabled
    return {
        "status": "ok",
        "offline_mode_enabled": settings.OFFLINE_MODE_ENABLED,
    }
