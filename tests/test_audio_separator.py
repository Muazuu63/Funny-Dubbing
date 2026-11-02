"""
Unit tests for Demucs Stem Splitter and Master Audio Backup Preservation (Phase 6.1).
"""
import pytest
from pathlib import Path
from app.engines.audio_separator import AudioSeparatorEngine, DEMUCS_LIMITATION_DISCLAIMER


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_master_audio_extraction_and_preservation(tmp_path):
    """Verify master original audio is extracted and preserved as master_audio.wav."""
    engine = AudioSeparatorEngine()
    video_file = tmp_path / "sample_video.mp4"
    video_file.write_bytes(b"MOCK_MP4_VIDEO_HEADER")

    out_dir = tmp_path / "audio_out"
    master_path = await engine.extract_master_audio(video_file, out_dir)

    assert master_path.is_file()
    assert master_path.name == "master_audio.wav"
    assert master_path.stat().st_size > 0


@pytest.mark.anyio
async def test_stem_separation_creates_both_stems_and_disclaimer(tmp_path):
    """Verify stem separation creates vocals and accompaniment and attaches limitation disclaimer."""
    engine = AudioSeparatorEngine()
    master_audio = tmp_path / "master_audio.wav"
    master_audio.write_bytes(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x02\x00D\xac\x00\x00\x10\xb1\x02\x00\x04\x00\x10\x00data\x00\x00\x00\x00")

    out_dir = tmp_path / "stems_out"
    result = await engine.separate_stems(master_audio, out_dir)

    assert Path(result.vocals_path).is_file()
    assert Path(result.accompaniment_path).is_file()
    assert result.master_audio_path == str(master_audio.resolve())
    assert master_audio.is_file()  # Master audio MUST still exist
    assert DEMUCS_LIMITATION_DISCLAIMER in result.disclaimer
