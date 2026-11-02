"""
Unit tests for Audio Speed-Stretch Pacing Engine & Dialogue Safety (Phase 6.2).
"""
import pytest
from pathlib import Path
from app.engines.timing_sync import (
    TimingSyncEngine,
    AudioTimingOverflowWarning,
    MIN_SPEED_MULTIPLIER,
    MAX_SPEED_MULTIPLIER,
)


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_speed_multiplier_bounds():
    """Verify playback pacing multipliers strictly stay within [0.85x, 1.25x]."""
    engine = TimingSyncEngine()

    # Normal case: 4.0s dialogue in 4.0s slot -> 1.0x
    mult, overflow = engine.calculate_pacing_multiplier(4.0, 4.0)
    assert mult == 1.0
    assert overflow == 0.0

    # Slight slow down: 3.5s dialogue in 4.0s slot -> 0.875x
    mult, overflow = engine.calculate_pacing_multiplier(3.5, 4.0)
    assert 0.85 <= mult <= 1.0
    assert overflow == 0.0

    # Very short dialogue: capped at MIN_SPEED_MULTIPLIER (0.85x)
    mult, overflow = engine.calculate_pacing_multiplier(1.0, 5.0)
    assert mult == MIN_SPEED_MULTIPLIER
    assert overflow == 0.0

    # Very long dialogue: capped at MAX_SPEED_MULTIPLIER (1.25x) with overflow
    mult, overflow = engine.calculate_pacing_multiplier(10.0, 4.0)
    assert mult == MAX_SPEED_MULTIPLIER
    # At 1.25x, 10s audio takes 8s -> overflow in 4s slot is 4.0s
    assert overflow == 4.0


@pytest.mark.anyio
async def test_timing_overflow_raises_warning(tmp_path):
    """Verify dialogue exceeding slot at max speed raises AudioTimingOverflowWarning to prevent auto-trimming."""
    engine = TimingSyncEngine()
    test_audio = tmp_path / "dialogue.wav"
    test_audio.write_bytes(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x02\x00D\xac\x00\x00\x10\xb1\x02\x00\x04\x00\x10\x00data\x00\x00\x00\x00")
    out_audio = tmp_path / "synced.wav"

    # Audio is 10.0s, slot is only 4.0s (overflows by 4.0s at 1.25x)
    with pytest.raises(AudioTimingOverflowWarning, match="Audio timing overflow"):
        await engine.apply_atempo_sync(
            input_audio_path=test_audio,
            output_audio_path=out_audio,
            audio_duration=10.0,
            slot_duration=4.0,
            force_allow_overflow=False,
        )

    # If force_allow_overflow is True (user explicitly approved), passes
    mult = await engine.apply_atempo_sync(
        input_audio_path=test_audio,
        output_audio_path=out_audio,
        audio_duration=10.0,
        slot_duration=4.0,
        force_allow_overflow=True,
    )
    assert mult == MAX_SPEED_MULTIPLIER
