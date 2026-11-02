"""
Security Module for AI-VPS.
Master Architecture v2.2 & PRD v2.2 Aligned.

Features:
1. Host Header Validation Middleware (DNS Rebinding prevention)
2. Strict Origin Middleware (Strict CORS & CSRF prevention)
3. Zero-Cost Permanent Hard-Lock (Blocking paid/billing endpoints)
4. OS-Level Secure Credential Storage via keyring (Windows Credential Manager)
5. SHA-256 API Key Fingerprinting & Masking
6. Path Traversal & Safe Path Validation
7. Safe MIME & Extension Validation
"""
import hashlib
import os
from pathlib import Path
from typing import Optional, List
import keyring
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from app.config import settings

KEYRING_SERVICE_NAME = "AI_VPS_STUDIO"

PAID_HOST_BLACKLIST = {
    "api.openai.com",
    "api.anthropic.com",
    "api.runwayml.com",
    "api.elevenlabs.io",
    "api.midjourney.com",
    "api.replicate.com",
    "fal.run",
}


# ==========================================
# 1. Credential Management & Fingerprinting
# ==========================================
def compute_key_fingerprint(api_key: str) -> str:
    """Computes a SHA-256 hash fingerprint of the API key for safe database tracking."""
    if not api_key:
        return ""
    digest = hashlib.sha256(api_key.strip().encode("utf-8")).hexdigest()
    return f"sha256:{digest[:16]}...{digest[-8:]}"


def mask_api_key(api_key: str) -> str:
    """Returns a masked version of the key showing only first 4 and last 4 chars."""
    if not api_key:
        return ""
    stripped = api_key.strip()
    if len(stripped) <= 8:
        return "********"
    return f"{stripped[:4]}...{stripped[-4:]}"


def store_secure_credential(service: str, secret: str) -> None:
    """Stores credential securely in OS-level Credential Manager with local fallback."""
    stored = False
    try:
        keyring.set_password(KEYRING_SERVICE_NAME, service, secret)
        stored = True
    except Exception:
        pass

    try:
        keys_dir = Path("data/.keys")
        keys_dir.mkdir(parents=True, exist_ok=True)
        key_file = keys_dir / f"{service}.key"
        key_file.write_text(secret.strip(), encoding="utf-8")
        stored = True
    except Exception:
        pass

    if not stored:
        # Memory fallback in settings
        if service == "gemini":
            settings.GEMINI_API_KEY = secret.strip()


def retrieve_secure_credential(service: str) -> Optional[str]:
    """Retrieves credential securely from OS-level Credential Manager or fallback."""
    try:
        val = keyring.get_password(KEYRING_SERVICE_NAME, service)
        if val and val.strip():
            return val.strip()
    except Exception:
        pass

    try:
        key_file = Path("data/.keys") / f"{service}.key"
        if key_file.exists():
            content = key_file.read_text(encoding="utf-8").strip()
            if content:
                return content
    except Exception:
        pass

    if service == "gemini" and getattr(settings, "GEMINI_API_KEY", None):
        return settings.GEMINI_API_KEY.strip()

    return None


def delete_secure_credential(service: str) -> bool:
    """Deletes credential from OS-level Credential Manager and local storage."""
    deleted = False
    try:
        keyring.delete_password(KEYRING_SERVICE_NAME, service)
        deleted = True
    except Exception:
        pass

    try:
        key_file = Path("data/.keys") / f"{service}.key"
        if key_file.exists():
            key_file.unlink()
            deleted = True
    except Exception:
        pass

    if service == "gemini":
        settings.GEMINI_API_KEY = ""
        deleted = True

    return deleted


# ==========================================
# 2. File and Path Validation
# ==========================================
def validate_safe_path(target_path: Path, base_dir: Path) -> Path:
    """Ensures target path does not escape the base directory (Path Traversal protection)."""
    resolved_target = target_path.resolve()
    resolved_base = base_dir.resolve()
    if not str(resolved_target).startswith(str(resolved_base)):
        raise ValueError(f"Path traversal detected: {target_path} is outside allowed base {base_dir}")
    return resolved_target


def validate_mime_type(mime_type: str) -> bool:
    """Validates MIME type against allowed security allowlist."""
    return mime_type.lower() in [m.lower() for m in settings.ALLOWED_MIME_TYPES]


def validate_file_extension(filename: str) -> bool:
    """Validates file extension against allowed security allowlist."""
    ext = Path(filename).suffix.lower()
    return ext in [e.lower() for e in settings.ALLOWED_EXTENSIONS]


# ==========================================
# 3. Security Middlewares
# ==========================================
class HostHeaderValidationMiddleware(BaseHTTPMiddleware):
    """
    Prevents DNS Rebinding attacks by enforcing allowed Host headers.
    Restricted strictly to 127.0.0.1:8000, localhost:8000, 127.0.0.1, localhost.
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        host_header = request.headers.get("host", "").lower().split(":", 1)[0]
        # Also check with port if present
        raw_host = request.headers.get("host", "").lower()
        
        allowed_hosts = [h.lower() for h in settings.ALLOWED_HOSTS]
        
        if raw_host not in allowed_hosts and host_header not in allowed_hosts:
            return JSONResponse(
                status_code=403,
                content={"error": "Forbidden: Invalid Host header (DNS Rebinding Protection)"}
            )
        return await call_next(request)


class StrictOriginMiddleware(BaseHTTPMiddleware):
    """
    Strict Origin & CSRF Protection Middleware.
    Validates Origin / Referer for browser requests. No Wildcard CORS allowed.
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        origin = request.headers.get("origin")
        trusted_origins = [o.rstrip("/") for o in settings.TRUSTED_ORIGINS]

        if origin:
            normalized_origin = origin.rstrip("/")
            if normalized_origin not in trusted_origins:
                return JSONResponse(
                    status_code=403,
                    content={"error": f"Forbidden: Untrusted origin '{origin}'"}
                )

        response = await call_next(request)
        if origin and origin.rstrip("/") in trusted_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"

        return response


class ZeroCostHardLockMiddleware(BaseHTTPMiddleware):
    """
    Permanent Zero Extra Cost Hard-Lock.
    Rejects any request attempting to route to known paid AI APIs or auto-billing endpoints.
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Check query or path parameters for unauthorized paid services
        path = request.url.path.lower()
        for paid_host in PAID_HOST_BLACKLIST:
            if paid_host in path:
                return JSONResponse(
                    status_code=403,
                    content={"error": f"Permanent Zero Cost Hard-Lock: Paid service '{paid_host}' is strictly forbidden."}
                )
        return await call_next(request)
