"""
Unit tests for FastAPI Master Server REST & WebSocket Endpoints (Phase 11).
Tests: Health Check, Projects CRUD, Production Modes List, Settings & Key Management, WebSocket Event Streaming.
"""
import pytest
from starlette.testclient import TestClient

from app.main import app
from app.config import settings


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_health_check_and_root_endpoint():
    """Verify health check and single-port 127.0.0.1:8000 binding details."""
    client = TestClient(app)

    # Health check
    res = client.get("/api/v1/health", headers={"Host": "127.0.0.1:8000"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert data["host"] == "127.0.0.1"
    assert data["port"] == 8000

    # Root endpoint
    root_res = client.get("/", headers={"Host": "127.0.0.1:8000"})
    assert root_res.status_code == 200


def test_production_modes_catalog():
    """Verify 11 production modes listing with P1 to P4 phases."""
    client = TestClient(app)
    res = client.get("/api/v1/modes/", headers={"Host": "127.0.0.1:8000"})
    assert res.status_code == 200
    modes = res.json()["modes"]
    assert len(modes) == 11

    # Verify P1 active modes
    active_modes = [m for m in modes if m["phase"] == "P1"]
    assert len(active_modes) == 3


def test_projects_rest_crud_lifecycle():
    """Verify creating, retrieving details, and deleting a project via REST API."""
    client = TestClient(app)

    # Create project
    create_payload = {
        "title": "REST API Dubbing Project",
        "mode": "mode01_dubbing",
        "targetLanguages": ["Bangla", "Hindi"],
    }
    create_res = client.post("/api/v1/projects/", json=create_payload, headers={"Host": "127.0.0.1:8000"})
    assert create_res.status_code == 200
    created = create_res.json()
    project_id = created["id"]
    assert created["title"] == "REST API Dubbing Project"

    # List projects
    list_res = client.get("/api/v1/projects/", headers={"Host": "127.0.0.1:8000"})
    assert list_res.status_code == 200
    assert any(p["id"] == project_id for p in list_res.json())

    # Get project details (includes mixer state)
    detail_res = client.get(f"/api/v1/projects/{project_id}", headers={"Host": "127.0.0.1:8000"})
    assert detail_res.status_code == 200
    details = detail_res.json()
    assert details["project"]["id"] == project_id
    # AudioMixerState uses TypeScript camelCase alias (masterVolume)
    assert details["mixer_state"].get("masterVolume") == 1.0 or details["mixer_state"].get("master_volume") == 1.0

    # Delete project
    del_res = client.delete(f"/api/v1/projects/{project_id}", headers={"Host": "127.0.0.1:8000"})
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "ok"


def test_settings_and_key_management():
    """Verify settings retrieval, RAM metrics, and secure API key storage."""
    client = TestClient(app)

    # Get settings
    settings_res = client.get("/api/v1/settings/", headers={"Host": "127.0.0.1:8000"})
    assert settings_res.status_code == 200
    data = settings_res.json()
    assert "verified_free_models" in data
    assert "system_memory" in data
    assert data["system_memory"]["total_gb"] > 0

    # Save key
    key_payload = {"api_key": "AIzaSyD-SecureTestKey1234567890"}
    save_res = client.post("/api/v1/settings/gemini-key", json=key_payload, headers={"Host": "127.0.0.1:8000"})
    assert save_res.status_code == 200
    save_data = save_res.json()
    assert save_data["status"] == "SAVED_SECURELY"
    assert "sha256:" in save_data["api_key_fingerprint"]
    assert "..." in save_data["api_key_masked"]
    # Plaintext key must NOT be returned in response!
    assert "api_key" not in save_data

    # Clean up test key so it does not interfere with runtime
    del_res = client.delete("/api/v1/settings/gemini-key", headers={"Host": "127.0.0.1:8000"})
    assert del_res.status_code == 200

    # Toggle offline mode
    toggle_res = client.post("/api/v1/settings/offline-mode", json={"enabled": True}, headers={"Host": "127.0.0.1:8000"})
    assert toggle_res.status_code == 200
    assert toggle_res.json()["offline_mode_enabled"] is True

    # Revert offline mode
    client.post("/api/v1/settings/offline-mode", json={"enabled": False}, headers={"Host": "127.0.0.1:8000"})


def test_websocket_event_streaming():
    """Verify live WebSocket event stream handshake and ping-pong responsiveness."""
    client = TestClient(app)
    with client.websocket_connect("/ws/events", headers={"Host": "127.0.0.1:8000"}) as ws:
        # Read handshake
        initial_event = ws.receive_json()
        assert initial_event["event"] == "CONNECTED"
        assert "Live Event Stream" in initial_event["message"]

        # Send ping
        ws.send_text("ping")
        resp = ws.receive_text()
        assert resp == "pong"
