"""
Unit tests to verify production built Vite + React frontend serving via FastAPI (Phase 12).
Verifies index.html, static asset files, and single-port 127.0.0.1:8000 lock.
"""
import pytest
from starlette.testclient import TestClient
from app.main import app
from app.config import settings


def test_built_frontend_served_at_root():
    """Verify that root GET / serves the compiled React app from frontend/dist."""
    client = TestClient(app)
    res = client.get("/", headers={"Host": "127.0.0.1:8000"})
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert ("Muazu Studio" in res.text or "AI-VPS Studio" in res.text)
    assert "<div id=\"root\"></div>" in res.text


def test_built_frontend_assets_exist():
    """Verify built assets in frontend/dist/assets can be retrieved."""
    dist_dir = settings.FRONTEND_DIST_DIR
    assets_dir = dist_dir / "assets"
    assert dist_dir.exists(), "frontend/dist should exist after npm run build"
    assert assets_dir.exists(), "frontend/dist/assets should exist"

    asset_files = list(assets_dir.glob("*.js"))
    assert len(asset_files) > 0, "At least one compiled JS bundle should exist"

    js_file = asset_files[0]
    client = TestClient(app)
    res = client.get(f"/assets/{js_file.name}", headers={"Host": "127.0.0.1:8000"})
    assert res.status_code == 200
    assert ("application/javascript" in res.headers["content-type"] or
            "text/javascript" in res.headers["content-type"])
