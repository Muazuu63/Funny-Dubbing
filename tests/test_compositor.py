"""
Unit tests for 4-Track Interactive Audio Mixer, Limiter & Clipping Guard (Phase 6.3).
"""
import pytest
from pathlib import Path
from app.engines.compositor import CompositorEngine, MixerTrackConfig


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_four_track_audio_mixing(tmp_path):
    """Verify 4 tracks mixing with Track 1 default muted."""
    engine = CompositorEngine()

    # Create 4 mock wav files
    wav_header = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x02\x00D\xac\x00\x00\x10\xb1\x02\x00\x04\x00\x10\x00data\x00\x00\x00\x00"
    t1_file = tmp_path / "original_backup.wav"
    t2_file = tmp_path / "demucs_vocals.wav"
    t3_file = tmp_path / "demucs_accompaniment.wav"
    t4_file = tmp_path / "ai_voice.wav"

    for f in (t1_file, t2_file, t3_file, t4_file):
        f.write_bytes(wav_header)

    tracks = {
        "original_backup": MixerTrackConfig(
            name="Original Backup",
            file_path=str(t1_file),
            volume=1.0,
            muted=True,  # Default MUTED to prevent echo
        ),
        "vocals": MixerTrackConfig(
            name="Demucs Vocals",
            file_path=str(t2_file),
            volume=0.9,
            muted=False,
        ),
        "accompaniment": MixerTrackConfig(
            name="Accompaniment",
            file_path=str(t3_file),
            volume=1.0,
            muted=False,
        ),
        "ai_voice": MixerTrackConfig(
            name="AI Voice",
            file_path=str(t4_file),
            volume=1.2,
            muted=False,
        ),
    }

    out_file = tmp_path / "final_mixed.wav"
    telemetry = await engine.mix_audio_tracks(
        tracks=tracks,
        output_path=out_file,
        master_volume=1.0,
        enable_limiter=True,
        enable_normalizer=True,
    )

    assert Path(telemetry.output_audio_path).is_file()
    assert telemetry.limiter_active is True
    assert telemetry.normalizer_lufs == -16.0
    assert -60.0 <= telemetry.master_level_dbfs <= 6.0


@pytest.mark.anyio
async def test_clipping_detection_telemetry(tmp_path):
    """Verify peak clipping detected flag when master level exceeds safe ceiling."""
    engine = CompositorEngine()
    empty_file = tmp_path / "silent.wav"
    empty_file.write_bytes(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x02\x00D\xac\x00\x00\x10\xb1\x02\x00\x04\x00\x10\x00data\x00\x00\x00\x00")

    tracks = {
        "track1": MixerTrackConfig(
            name="Loud Track",
            file_path=str(empty_file),
            volume=1.5,
        )
    }

    out_file = tmp_path / "loud_mixed.wav"
    # Mix with high master volume without normalizer to simulate extreme peak
    telemetry = await engine.mix_audio_tracks(
        tracks=tracks,
        output_path=out_file,
        master_volume=1.5,
        enable_limiter=False,
        enable_normalizer=False,
    )

    assert telemetry.peak_clipping_detected is True
