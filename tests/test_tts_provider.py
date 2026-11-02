"""
Unit tests for TTS Provider and Model Commercial License Registry (Phase 3.3).
"""
import pytest
from pathlib import Path
from app.config import settings, CommercialUseStatus
from app.providers.tts_provider import (
    TTSProvider,
    OfflineEngineBlockedError,
)
from app.providers.model_registry import (
    model_registry_manager,
    CommercialLicenseViolationError,
    HardwarePreflightError,
)


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_paid_engine_hardlock():
    """Verify that paid engines (e.g., ElevenLabs) are immediately rejected by Zero Cost Hard-Lock."""
    with pytest.raises(ValueError, match="Zero Extra Cost Policy"):
        TTSProvider(engine_id="elevenlabs")


@pytest.mark.anyio
async def test_edge_tts_blocked_in_offline_mode(tmp_path):
    """Verify that online Edge-TTS is strictly blocked when offline mode is enabled."""
    settings.OFFLINE_MODE_ENABLED = True
    out_file = tmp_path / "audio.wav"
    try:
        provider = TTSProvider(engine_id="edge-tts")
        assert provider.is_available() is False

        with pytest.raises(OfflineEngineBlockedError):
            await provider.synthesize(
                text="Hello funny world",
                output_path=str(out_file),
                is_commercial=False,
            )
    finally:
        settings.OFFLINE_MODE_ENABLED = False


@pytest.mark.anyio
async def test_commercial_license_gate_blocks_non_commercial_model(tmp_path):
    """
    Verify that CC-BY-NC models (like Meta MMS) are strictly blocked
    when commercial mode is enabled (is_commercial=True).
    """
    out_file = tmp_path / "audio.wav"
    provider = TTSProvider(engine_id="meta-mms-tts")

    # Commercial mode should raise CommercialLicenseViolationError
    with pytest.raises(CommercialLicenseViolationError, match="strictly forbidden"):
        await provider.synthesize(
            text="Testing license gate",
            output_path=str(out_file),
            is_commercial=True,
        )

    # Non-commercial mode should pass preflight gate and synthesize
    result_path = await provider.synthesize(
        text="Testing non-commercial",
        output_path=str(out_file),
        is_commercial=False,
    )
    assert Path(result_path).exists()


def test_checksum_verification(tmp_path):
    """Verify file SHA-256 calculation and checksum validation."""
    test_file = tmp_path / "model.weights"
    test_file.write_bytes(b"Model weights test binary data 1234567890")

    # Known sha256 for the string above:
    # echo -n "Model weights test binary data 1234567890" | sha256sum
    import hashlib
    expected_hash = hashlib.sha256(b"Model weights test binary data 1234567890").hexdigest()

    assert model_registry_manager.verify_file_checksum(test_file, expected_hash) is True
    assert model_registry_manager.verify_file_checksum(test_file, "wrong_hash_12345") is False
