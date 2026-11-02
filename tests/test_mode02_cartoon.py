"""
Unit tests for Mode 02 Cartoon & 2D Animation Studio (Phase 8).
Tests: Transcription fallback, Voice Approval Gateway, 1-Click Delta Audio Swap, 5-Language Matrix.
"""
import pytest
from pathlib import Path

from app.engines.transcriber import TranscriberEngine
from app.modes.mode02_cartoon import Mode02Cartoon, VoiceType
from app.modes.mode01_dubbing import VoiceApprovalRequiredError
from app.api.routes_approval import submit_voice_approval, ApprovalRequest, ApprovalAction


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_transcriber_manual_text_fallback():
    """Verify transcription falls back gracefully to manual script input with timestamp segments."""
    engine = TranscriberEngine()
    manual_script = "লাইন ১: কার্টুন কথা বলছে।\nলাইন ২: দ্বিতীয় চরিত্র দৌড়াচ্ছে।"

    res = await engine.transcribe_audio(
        audio_path=Path("dummy.wav"),
        manual_text=manual_script,
    )
    assert res.is_fallback is True
    assert res.engine_used == "Manual Text Input"
    assert len(res.segments) == 2
    assert res.segments[0].text == "লাইন ১: কার্টুন কথা বলছে।"
    assert res.segments[1].start == 3.0


@pytest.mark.anyio
async def test_mode02_approval_gateway_and_final_render(tmp_path):
    """Verify Mode 02 voice approval gateway blocks export until user approves."""
    mode02 = Mode02Cartoon()
    project_dir = tmp_path / "cartoon_proj_01"
    project_dir.mkdir()

    input_video = project_dir / "cartoon_input.mp4"
    input_video.write_bytes(b"MOCK_CARTOON_SOURCE_VIDEO")
    proj_id = "cartoon-proj-approval-01"

    # Step 1: Execute preview
    preview_res = await mode02.execute_preview(
        project_id=proj_id,
        input_video_path=input_video,
        project_dir=project_dir,
        voice_type=VoiceType.AI_VOICE,
    )
    assert preview_res["status"] == "WAITING_FOR_VOICE_APPROVAL"
    assert Path(preview_res["preview_audio"]).is_file()

    # Final render without approval must raise VoiceApprovalRequiredError
    with pytest.raises(VoiceApprovalRequiredError):
        await mode02.execute_final_render(
            project_id=proj_id,
            project_dir=project_dir,
            voice_type=VoiceType.AI_VOICE,
            language_matrix_choice="Bangla",
        )

    # Approve voice
    await submit_voice_approval(proj_id, ApprovalRequest(action=ApprovalAction.APPROVE))

    # Render succeeds
    outputs = await mode02.execute_final_render(
        project_id=proj_id,
        project_dir=project_dir,
        voice_type=VoiceType.AI_VOICE,
        language_matrix_choice="Bangla",
    )
    assert len(outputs) == 1
    assert outputs[0].name == "cartoon_output_Bangla.mp4"
    assert outputs[0].is_file()


@pytest.mark.anyio
async def test_one_click_delta_audio_swap(tmp_path):
    """Verify 1-Click Delta Audio Swap instantly replaces audio track using cached video stream."""
    mode02 = Mode02Cartoon()
    project_dir = tmp_path / "cartoon_delta_proj"
    project_dir.mkdir()

    input_video = project_dir / "source.mp4"
    input_video.write_bytes(b"MOCK_CARTOON_FRAMES")
    proj_id = "delta-swap-01"

    # Preview to populate cache
    await mode02.execute_preview(proj_id, input_video, project_dir, voice_type=VoiceType.AI_VOICE)

    # 1-Click Delta swap from AI Voice to Real Voice
    swapped_file = await mode02.swap_audio_delta(
        project_dir=project_dir,
        new_voice_type=VoiceType.REAL_VOICE,
        target_language="Bangla",
    )
    assert swapped_file.is_file()
    assert swapped_file.name == "cartoon_output_Bangla.mp4"


@pytest.mark.anyio
async def test_mode02_five_language_matrix(tmp_path):
    """Verify Mode 02 handles multi-language export for 'Bangla + Hindi' (2 files)."""
    mode02 = Mode02Cartoon()
    project_dir = tmp_path / "cartoon_multi_lang"
    project_dir.mkdir()

    input_video = project_dir / "source.mp4"
    input_video.write_bytes(b"MOCK_CARTOON_FRAMES")
    proj_id = "multi-lang-02"

    await mode02.execute_preview(proj_id, input_video, project_dir)
    await submit_voice_approval(proj_id, ApprovalRequest(action=ApprovalAction.APPROVE))

    outputs = await mode02.execute_final_render(
        project_id=proj_id,
        project_dir=project_dir,
        language_matrix_choice="Bangla + Hindi",
    )
    assert len(outputs) == 2
    names = [f.name for f in outputs]
    assert "cartoon_output_Bangla.mp4" in names
    assert "cartoon_output_Hindi.mp4" in names
