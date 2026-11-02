"""
Unit tests for Gemini Provider, 3-Status Fail-Safe, and Local Fallback Engine (Phase 3.2).
"""
import pytest
from unittest.mock import patch, MagicMock
from app.config import settings, GeminiVerificationStatus
from app.providers.gemini_provider import (
    GeminiProvider,
    LocalScriptEngine,
    RateLimitPausedException,
)
from app.providers.base import PrivacyConsentData


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_quad_check_verified_free():
    """Verify that officially known free models are marked VERIFIED_FREE."""
    provider = GeminiProvider(api_key="AIzaSyMockKeyForTesting")
    result = await provider.quad_check("gemini-1.5-flash")

    assert result.status == GeminiVerificationStatus.VERIFIED_FREE
    assert result.model_availability is True
    assert result.free_tier_eligibility == "ELIGIBLE_FREE"
    assert result.billing_configuration == "UNKNOWN"
    assert result.remaining_quota == "UNKNOWN"


@pytest.mark.anyio
async def test_quad_check_unverified_model_fails_closed():
    """Verify unverified or paid models fail-closed to UNAVAILABLE."""
    provider = GeminiProvider(api_key="AIzaSyMockKeyForTesting")
    result = await provider.quad_check("gemini-ultra-paid")

    assert result.status == GeminiVerificationStatus.UNAVAILABLE
    assert result.free_tier_eligibility == "UNKNOWN"


@pytest.mark.anyio
async def test_privacy_consent_gate():
    """Verify cloud call is blocked and falls back to local engine without user consent."""
    provider = GeminiProvider(api_key="AIzaSyMockKeyForTesting")
    
    # Missing consent
    result = await provider.generate_script(
        prompt="A cat jumping on a sofa",
        target_language="Bangla",
        privacy_consent=None,
    )
    assert result.is_fallback is True
    assert result.provider_name == "LocalScriptEngine"
    assert len(result.scenes) > 0


@pytest.mark.anyio
async def test_offline_mode_blocking():
    """Verify that offline mode blocks cloud calls completely."""
    settings.OFFLINE_MODE_ENABLED = True
    try:
        provider = GeminiProvider(api_key="AIzaSyMockKeyForTesting")
        quad_result = await provider.quad_check("gemini-1.5-flash")
        assert quad_result.status == GeminiVerificationStatus.UNAVAILABLE

        gen_result = await provider.generate_script(
            prompt="Funny moment",
            target_language="Bangla",
            privacy_consent=PrivacyConsentData(user_consent_granted=True),
        )
        assert gen_result.is_fallback is True
        assert gen_result.provider_name == "LocalScriptEngine"
    finally:
        settings.OFFLINE_MODE_ENABLED = False


@pytest.mark.anyio
async def test_rate_limit_telemetry_raises_paused_exception():
    """Verify HTTP 429 raises RateLimitPausedException with retry_after."""
    provider = GeminiProvider(api_key="AIzaSyMockKeyForTesting")
    consent = PrivacyConsentData(
        user_consent_granted=True,
        data_types_shared=["Text"]
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_resp.headers = {"Retry-After": "45"}

    with patch("requests.post", return_value=mock_resp):
        with pytest.raises(RateLimitPausedException) as exc_info:
            await provider.generate_script(
                prompt="Funny dog chasing ball",
                target_language="Bangla",
                privacy_consent=consent,
            )
        assert exc_info.value.retry_after == 45
        assert "PAUSED" in str(exc_info.value)
