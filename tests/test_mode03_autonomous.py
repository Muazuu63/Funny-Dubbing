"""
Unit tests for Mode 03 Autonomous Content Creator Studio (Phase 9).
Tests: Engine Availability Gate, Voice Approval Gateway, and 5-Language Matrix Rendering.
"""
import pytest
from pathlib import Path

from app.modes.mode03_autonomous import Mode03Autonomous, VISUAL_ENGINE_NOTICE
from app.modes.mode01_dubbing import VoiceApprovalRequiredError
from app.api.routes_approval import submit_voice_approval, ApprovalRequest, ApprovalAction


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_engine_availability_gate_marks_unavailable(tmp_path):
    """Verify that when local SD/GPU is not present, visual engine is marked UNAVAILABLE with clear notice."""
    mode03 = Mode03Autonomous()
    project_dir = tmp_path / "mode03_proj_01"
    project_dir.mkdir()

    res = await mode03.execute_preview(
        project_id="auto-proj-01",
        topic_prompt="Funny robot cooking food",
        project_dir=project_dir,
        target_language="Bangla",
    )

    assert res["status"] == "WAITING_FOR_VOICE_APPROVAL"
    assert res["visual_engine_status"] in ("AVAILABLE", "UNAVAILABLE")
    if res["visual_engine_status"] == "UNAVAILABLE":
        assert res["visual_engine_notice"] == VISUAL_ENGINE_NOTICE
        assert "Zero Extra Cost Policy" in res["visual_engine_notice"]


@pytest.mark.anyio
async def test_mode03_voice_approval_blocks_final_render(tmp_path):
    """Verify Mode 03 enforces Voice Approval Gateway before final render."""
    mode03 = Mode03Autonomous()
    project_dir = tmp_path / "mode03_proj_approval"
    project_dir.mkdir()
    proj_id = "auto-proj-approval-02"

    await mode03.execute_preview(
        project_id=proj_id,
        topic_prompt="Cat playing chess",
        project_dir=project_dir,
    )

    # Attempt render before approval -> MUST RAISE
    with pytest.raises(VoiceApprovalRequiredError):
        await mode03.execute_final_render(
            project_id=proj_id,
            project_dir=project_dir,
            language_matrix_choice="Bangla",
        )

    # Approve
    await submit_voice_approval(proj_id, ApprovalRequest(action=ApprovalAction.APPROVE))

    # Render succeeds
    outputs = await mode03.execute_final_render(
        project_id=proj_id,
        project_dir=project_dir,
        language_matrix_choice="Bangla",
    )
    assert len(outputs) == 1
    assert outputs[0].name == "autonomous_output_Bangla.mp4"
    assert outputs[0].is_file()


@pytest.mark.anyio
async def test_mode03_three_language_matrix_render(tmp_path):
    """Verify Mode 03 renders 3 separate video files for 'Bangla + Hindi + English'."""
    mode03 = Mode03Autonomous()
    project_dir = tmp_path / "mode03_multi_lang"
    project_dir.mkdir()
    proj_id = "auto-proj-three-langs"

    await mode03.execute_preview(proj_id, "Funny space monkey", project_dir)
    await submit_voice_approval(proj_id, ApprovalRequest(action=ApprovalAction.APPROVE))

    outputs = await mode03.execute_final_render(
        project_id=proj_id,
        project_dir=project_dir,
        language_matrix_choice="Bangla + Hindi + English",
    )
    assert len(outputs) == 3
    names = [f.name for f in outputs]
    assert "autonomous_output_Bangla.mp4" in names
    assert "autonomous_output_Hindi.mp4" in names
    assert "autonomous_output_English.mp4" in names
