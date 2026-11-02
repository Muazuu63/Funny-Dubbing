"""
Unit tests for AI-VPS Security Module (Phase 3.1).
"""
import pytest
from pathlib import Path
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from app.core.security import (
    HostHeaderValidationMiddleware,
    StrictOriginMiddleware,
    ZeroCostHardLockMiddleware,
    compute_key_fingerprint,
    mask_api_key,
    store_secure_credential,
    retrieve_secure_credential,
    delete_secure_credential,
    validate_safe_path,
    validate_mime_type,
    validate_file_extension,
)


async def sample_endpoint(request):
    return JSONResponse({"status": "ok"})


def create_test_app():
    app = Starlette(routes=[Route("/test", sample_endpoint)])
    app.add_middleware(ZeroCostHardLockMiddleware)
    app.add_middleware(StrictOriginMiddleware)
    app.add_middleware(HostHeaderValidationMiddleware)
    return app


def test_host_header_validation():
    """Verify Host Header allowlist and rejection of unauthorized hosts."""
    app = create_test_app()
    client = TestClient(app)

    # Valid Host headers
    res = client.get("/test", headers={"Host": "127.0.0.1:8000"})
    assert res.status_code == 200

    res = client.get("/test", headers={"Host": "localhost:8000"})
    assert res.status_code == 200

    # Malicious Host header (DNS Rebinding)
    res = client.get("/test", headers={"Host": "attacker.com"})
    assert res.status_code == 403
    assert "Invalid Host header" in res.json()["error"]


def test_strict_origin_cors():
    """Verify Origin validation and absence of wildcard CORS."""
    app = create_test_app()
    client = TestClient(app)

    # Trusted origin
    res = client.get(
        "/test",
        headers={"Host": "127.0.0.1:8000", "Origin": "http://127.0.0.1:8000"}
    )
    assert res.status_code == 200
    assert res.headers["Access-Control-Allow-Origin"] == "http://127.0.0.1:8000"

    # Tauri origin
    res = client.get(
        "/test",
        headers={"Host": "127.0.0.1:8000", "Origin": "tauri://localhost"}
    )
    assert res.status_code == 200

    # Untrusted origin
    res = client.get(
        "/test",
        headers={"Host": "127.0.0.1:8000", "Origin": "http://evil-site.com"}
    )
    assert res.status_code == 403
    assert "Untrusted origin" in res.json()["error"]


def test_credential_storage_and_masking():
    """Verify secure credential storage via keyring, masking and SHA-256 fingerprinting."""
    test_key = "AIzaSyD-TestKey1234567890ABCDEF"
    
    # Fingerprint & Masking
    fingerprint = compute_key_fingerprint(test_key)
    assert fingerprint.startswith("sha256:")
    assert test_key not in fingerprint

    masked = mask_api_key(test_key)
    assert masked.startswith("AIza")
    assert masked.endswith("CDEF")
    assert "..." in masked

    # Storage operations
    store_secure_credential("test_gemini", test_key)
    retrieved = retrieve_secure_credential("test_gemini")
    assert retrieved == test_key

    deleted = delete_secure_credential("test_gemini")
    assert deleted is True


def test_path_traversal_protection(tmp_path):
    """Verify that path traversal attempts are detected and rejected."""
    base_dir = tmp_path / "storage"
    base_dir.mkdir()
    safe_file = base_dir / "project1" / "video.mp4"
    safe_file.parent.mkdir()
    safe_file.touch()

    # Safe access
    resolved = validate_safe_path(safe_file, base_dir)
    assert resolved == safe_file.resolve()

    # Traversal attempt
    unsafe_file = base_dir / ".." / "secret.txt"
    with pytest.raises(ValueError, match="Path traversal detected"):
        validate_safe_path(unsafe_file, base_dir)


def test_mime_and_extension_validation():
    """Verify media MIME types and extension security allowlists."""
    assert validate_mime_type("video/mp4") is True
    assert validate_mime_type("audio/wav") is True
    assert validate_mime_type("application/x-executable") is False

    assert validate_file_extension("movie.mp4") is True
    assert validate_file_extension("audio.wav") is True
    assert validate_file_extension("virus.exe") is False
