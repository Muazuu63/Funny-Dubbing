"""
Unit tests for Mode 01 Fast Funny Dubbing Pipeline (Phase 7).
Tests: Inpainting, Voice Approval Gateway, and 5-Language Matrix Rendering.
"""
import pytest
from pathlib import Path
import numpy as np

from app.engines.inpainter import InpainterEngine
from app.modes.mode01_dubbing import Mode01Dubbing, VoiceApprovalRequiredError
from app.api.routes_approval import (
    submit_voice_approval,
    get_approval_status,
    ApprovalRequest,
    ApprovalAction,
)


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_opencv_inpainting_frame_and_warning():
    """Verify OpenCV CPU inpainting works and flags high mask coverage."""
    engine = InpainterEngine()

    # Create dummy 100x100 RGB frame
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[:, :] = [100, 150, 200]

    # Create mask covering 5% (safe)
    mask_small = np.zeros((100, 100), dtype=np.uint8)
    mask_small[10:20, 10:20] = 255  # 100 pixels out of 10,000 = 1%
    inpainted, warning = engine.inpaint_frame(frame, mask_small)
    assert inpainted.shape == frame.shape
    assert warning is None

    # Create mask covering 25% (> 15% threshold)
    mask_large = np.zeros((100, 100), dtype=np.uint8)
    mask_large[0:50, 0:50] = 255  # 2500 pixels out of 10,000 = 25%
    inpainted_large, warning_large = engine.inpaint_frame(frame, mask_large)
    assert warning_large is not None
    assert "High mask coverage" in warning_large


@pytest.mark.anyio
async def test_universal_voice_approval_gateway_blocks_render(tmp_path):
    """Verify final render is strictly blocked until user explicitly approves the voice."""
    mode01 = Mode01Dubbing()
    project_dir = tmp_path / "proj_dubbing_01"
    project_dir.mkdir()

    input_video = project_dir / "input.mp4"
    input_video.write_bytes(b"MOCK_MP4_SOURCE_VIDEO")

    project_id = "test-project-approval-01"

    # Step 1-4: Generate preview
    preview_res = await mode01.execute_step_preview(
        project_id=project_id,
        input_video_path=input_video,
        project_dir=project_dir,
        target_language_matrix="Bangla",
    )
    assert preview_res["status"] == "WAITING_FOR_VOICE_APPROVAL"

    # Attempt to render final video without approval -> MUST RAISE VoiceApprovalRequiredError
    with pytest.raises(VoiceApprovalRequiredError, match="Voice Approval Required"):
        await mode01.execute_final_render(
            project_id=project_id,
            input_video_path=input_video,
            project_dir=project_dir,
            language_matrix_choice="Bangla",
        )

    # User submits approval via approval gateway
    approved = await submit_voice_approval(
        project_id=project_id,
        payload=ApprovalRequest(action=ApprovalAction.APPROVE, notes="Voice sounds funny and clear!"),
    )
    assert approved.status == "APPROVED"

    # Now final render succeeds
    output_files = await mode01.execute_final_render(
        project_id=project_id,
        input_video_path=input_video,
        project_dir=project_dir,
        language_matrix_choice="Bangla",
    )
    assert len(output_files) == 1
    assert output_files[0].name == "output_Bangla.mp4"
    assert output_files[0].is_file()


@pytest.mark.anyio
async def test_five_language_matrix_multi_render(tmp_path):
    """Verify exact 5-language matrix produces 1, 2, or 3 separate video files."""
    mode01 = Mode01Dubbing()
    project_dir = tmp_path / "proj_dubbing_matrix"
    project_dir.mkdir()

    input_video = project_dir / "input.mp4"
    input_video.write_bytes(b"MOCK_MP4_SOURCE_VIDEO")

    # 1. Test "Bangla + Hindi" -> 2 files
    proj_id_2 = "proj-matrix-2"
    await mode01.execute_step_preview(proj_id_2, input_video, project_dir)
    await submit_voice_approval(proj_id_2, ApprovalRequest(action=ApprovalAction.APPROVE))

    outputs_2 = await mode01.execute_final_render(
        project_id=proj_id_2,
        input_video_path=input_video,
        project_dir=project_dir,
        language_matrix_choice="Bangla + Hindi",
    )
    assert len(outputs_2) == 2
    filenames_2 = [f.name for f in outputs_2]
    assert "output_Bangla.mp4" in filenames_2
    assert "output_Hindi.mp4" in filenames_2

    # 2. Test "Bangla + Hindi + English" -> 3 files
    proj_id_3 = "proj-matrix-3"
    await mode01.execute_step_preview(proj_id_3, input_video, project_dir)
    await submit_voice_approval(proj_id_3, ApprovalRequest(action=ApprovalAction.APPROVE))

    outputs_3 = await mode01.execute_final_render(
        project_id=proj_id_3,
        input_video_path=input_video,
        project_dir=project_dir,
        language_matrix_choice="Bangla + Hindi + English",
    )
    assert len(outputs_3) == 3
    filenames_3 = [f.name for f in outputs_3]
    assert "output_Bangla.mp4" in filenames_3
    assert "output_Hindi.mp4" in filenames_3
    assert "output_English.mp4" in filenames_3
