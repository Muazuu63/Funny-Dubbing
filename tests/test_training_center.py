"""
Unit tests for Layer 4: Shared Training Center Core & Reusable Asset Hub (Phase 10).
Tests: Profile CRUD, Preset Initialization, AI-Assisted Reference Analysis, API endpoints.
"""
import pytest
from pathlib import Path
from fastapi import FastAPI
from starlette.testclient import TestClient

from app.core.training_center import (
    TrainingCenterManager,
    TrainingProfile,
    TrainingProfileCategory,
)
from app.api.routes_training import router as training_router


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_built_in_presets_initialization(tmp_path):
    """Verify built-in presets (Dhaka slapstick, cartoon cadence, voice) are auto-initialized."""
    manager = TrainingCenterManager(profiles_dir=tmp_path / "profiles")
    profiles = manager.list_profiles()

    assert len(profiles) >= 3
    names = [p.name for p in profiles]
    assert "Dhaka Slapstick Comedy" in names
    assert "Classic Cartoon Cadence" in names
    assert "Sarcastic Bengali Narrator" in names


def test_profile_crud_and_category_filter(tmp_path):
    """Verify creating, filtering, retrieving, and deleting a training profile."""
    manager = TrainingCenterManager(profiles_dir=tmp_path / "profiles")

    custom_profile = TrainingProfile(
        name="Custom Meme Timing",
        category=TrainingProfileCategory.PUNCHLINE_TIMING,
        description="Meme timing with dramatic pause.",
        parameters={"punchline_pause_sec": 1.2, "dramatic_boom_sfx": True},
    )

    saved = manager.save_profile(custom_profile)
    assert saved.profile_id is not None

    # Retrieve
    fetched = manager.get_profile(saved.profile_id)
    assert fetched is not None
    assert fetched.name == "Custom Meme Timing"
    assert fetched.parameters["punchline_pause_sec"] == 1.2

    # Category filter
    filtered = manager.list_profiles(category=TrainingProfileCategory.PUNCHLINE_TIMING)
    assert any(p.profile_id == saved.profile_id for p in filtered)

    # Delete
    deleted = manager.delete_profile(saved.profile_id)
    assert deleted is True
    assert manager.get_profile(saved.profile_id) is None


def test_ai_assisted_reference_analysis(tmp_path):
    """Verify reference analysis extracts cadence without GPU backprop."""
    manager = TrainingCenterManager(profiles_dir=tmp_path / "profiles")
    valid_video = tmp_path / "ref_comedy.mp4"
    valid_video.write_bytes(b"MOCK_REFERENCE_COMEDY_VIDEO_STREAM")

    analysis = manager.analyze_reference_video(valid_video)
    assert analysis["reference_file"] == "ref_comedy.mp4"
    assert analysis["analysis_type"] == "AI-assisted reference analysis (No-Backprop)"
    assert analysis["recommended_pacing_multiplier"] > 1.0

    # Test corrupted 0-byte video
    corrupt_video = tmp_path / "corrupt.mp4"
    corrupt_video.touch()
    with pytest.raises(ValueError, match="corrupted or 0 bytes"):
        manager.analyze_reference_video(corrupt_video)

    # Test missing video
    with pytest.raises(FileNotFoundError):
        manager.analyze_reference_video(tmp_path / "non_existent.mp4")


def test_training_api_endpoints():
    """Verify REST endpoints for training profiles hub."""
    app = FastAPI()
    app.include_router(training_router)
    client = TestClient(app)

    # List profiles
    res = client.get("/api/v1/training/profiles")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    # Create profile
    payload = {
        "name": "API Comedy Style",
        "category": "comedy_style",
        "description": "Created via API",
        "parameters": {"speed": 1.05},
    }
    create_res = client.post("/api/v1/training/profiles", json=payload)
    assert create_res.status_code == 200
    profile_id = create_res.json()["profile_id"]

    # Get created profile
    get_res = client.get(f"/api/v1/training/profiles/{profile_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "API Comedy Style"

    # Delete created profile
    del_res = client.delete(f"/api/v1/training/profiles/{profile_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "ok"
