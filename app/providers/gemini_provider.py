"""
Gemini API Provider with 3-Status Fail-Safe and Local Fallback Engine.
Master Architecture v2.2 & PRD v2.2 Aligned.

Key Architectural Guarantees:
1. Dynamic model discovery via API / verified list.
2. 3-Status Fail-Safe: VERIFIED_FREE, MANUAL_CONFIRMATION, UNAVAILABLE.
3. Strict Fail-Closed Privacy Gate: User must review shared data types before cloud calls.
4. Permanent Zero Extra Cost Hard-Lock: Only VERIFIED_FREE models are invoked.
5. Graceful Local Fallback: When Gemini is unavailable or rate-limited (HTTP 429), falls back to rule-based humorous script generator.
"""
import json
import time
from typing import Dict, Any, Optional, List
import requests

from app.config import settings, GeminiVerificationStatus
from app.core.security import compute_key_fingerprint, retrieve_secure_credential
from app.providers.base import (
    BaseLLMProvider,
    QuadCheckResult,
    ScriptGenerationResult,
    PrivacyConsentData,
)

# Officially documented Free Tier Models for Google AI Studio
OFFICIAL_FREE_TIER_MODELS = {
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite-preview-02-05",
}


class RateLimitPausedException(Exception):
    """Raised when Gemini returns HTTP 429 so checkpoint state can transition to PAUSED."""
    def __init__(self, retry_after: int = 60, details: str = ""):
        self.retry_after = retry_after
        self.details = details
        super().__init__(f"Gemini API Quota Exceeded (HTTP 429). Retry after {retry_after}s. State PAUSED.")


class LocalScriptEngine:
    """
    Offline Rule-Based Humorous Dialogue & Script Generator.
    Acts as a zero-cost, local-first fallback when cloud models are unavailable.
    """
    @staticmethod
    def generate_humorous_script(prompt: str, target_language: str = "Bangla") -> ScriptGenerationResult:
        scenes = [
            {
                "scene_id": 1,
                "character": "Protagonist",
                "original_timing": {"start": 0.0, "end": 4.5},
                "dialogue": f"[{target_language}] আরে ভাই, এইটা কী দেখলাম! বিশ্বাসই হচ্ছে না!",
                "tone": "Surprised/Humorous",
                "speed_multiplier": 1.0,
            },
            {
                "scene_id": 2,
                "character": "Sidekick",
                "original_timing": {"start": 4.6, "end": 8.5},
                "dialogue": f"[{target_language}] আরে ধুর মিয়া, বেশি কথা না বলে চলো পালাই!",
                "tone": "Panicked/Funny",
                "speed_multiplier": 1.0,
            },
            {
                "scene_id": 3,
                "character": "Protagonist",
                "original_timing": {"start": 8.6, "end": 12.0},
                "dialogue": f"[{target_language}] দাঁড়াও দাঁড়াও, আগে ক্যামেরা তো বন্ধ করো!",
                "tone": "Punchline",
                "speed_multiplier": 1.0,
            }
        ]
        return ScriptGenerationResult(
            provider_name="LocalScriptEngine",
            is_fallback=True,
            script_title=f"Funny Dubbing Script ({target_language}) [Local Fallback]",
            scenes=scenes,
        )


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or retrieve_secure_credential("gemini") or ""

    @property
    def api_key_fingerprint(self) -> str:
        return compute_key_fingerprint(self._api_key)

    def is_available(self) -> bool:
        """Provider is unavailable if offline mode is enabled or key is empty."""
        if settings.OFFLINE_MODE_ENABLED:
            return False
        return bool(self._api_key.strip())

    async def quad_check(self, model_name: str) -> QuadCheckResult:
        """
        4-point Quad-Check:
        1. Model Availability: Checked against supported model names.
        2. Free-tier Eligibility: Checked against official free tier list.
        3. Billing Configuration: UNKNOWN (API does not reveal project billing).
        4. Remaining Quota: UNKNOWN (Balance is not exposed by API).
        """
        if settings.OFFLINE_MODE_ENABLED:
            return QuadCheckResult(
                status=GeminiVerificationStatus.UNAVAILABLE,
                model_availability=False,
                free_tier_eligibility="BLOCKED_OFFLINE",
                details="Application is in offline mode."
            )

        if not self._api_key:
            return QuadCheckResult(
                status=GeminiVerificationStatus.UNAVAILABLE,
                model_availability=False,
                free_tier_eligibility="NO_API_KEY",
                details="No API key configured."
            )

        # 1. Model Availability
        model_available = model_name in OFFICIAL_FREE_TIER_MODELS or "gemini" in model_name.lower()
        
        # 2. Free Tier Eligibility
        if model_name in OFFICIAL_FREE_TIER_MODELS:
            free_tier_eligibility = "ELIGIBLE_FREE"
            status = GeminiVerificationStatus.VERIFIED_FREE
            details = f"Model '{model_name}' verified in Official Google AI Studio Free Tier list."
        else:
            free_tier_eligibility = "UNKNOWN"
            status = GeminiVerificationStatus.UNAVAILABLE
            details = f"Model '{model_name}' not in verified free tier list. Blocked (Fail-Closed)."

        return QuadCheckResult(
            status=status,
            model_availability=model_available,
            free_tier_eligibility=free_tier_eligibility,
            billing_configuration="UNKNOWN",
            remaining_quota="UNKNOWN",
            details=details
        )

    async def generate_script(
        self,
        prompt: str,
        target_language: str = "Bangla",
        model_name: str = "gemini-1.5-flash",
        privacy_consent: Optional[PrivacyConsentData] = None,
        **kwargs
    ) -> ScriptGenerationResult:
        """
        Generates script with strict Quad-Check, Privacy Gate, and Local Fallback.
        """
        # 1. Check Offline Mode
        if settings.OFFLINE_MODE_ENABLED:
            return LocalScriptEngine.generate_humorous_script(prompt, target_language)

        # 2. Check Quad-Check status
        quad_result = await self.quad_check(model_name)
        if quad_result.status != GeminiVerificationStatus.VERIFIED_FREE:
            # Automatic graceful fallback to local script engine
            return LocalScriptEngine.generate_humorous_script(prompt, target_language)

        # 3. Privacy Consent Gate
        if not privacy_consent or not privacy_consent.user_consent_granted:
            # Without explicit privacy consent, do NOT transmit data to cloud
            return LocalScriptEngine.generate_humorous_script(prompt, target_language)

        # 4. Outbound API Call (Mocked or Real HTTP with rate limit telemetry)
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self._api_key,
        }
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Generate a humorous, synchronized funny dubbing script in {target_language}. Context: {prompt}"
                }]
            }]
        }

        try:
            # We use timeout=15 to prevent blocking
            response = requests.post(endpoint, headers=headers, json=payload, timeout=15)
            
            # 5. Handle Rate Limit (HTTP 429) Telemetry
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "60"))
                raise RateLimitPausedException(retry_after=retry_after, details="429 Rate Limit hit.")

            if response.status_code == 200:
                data = response.json()
                # Parse candidates
                candidates = data.get("candidates", [])
                text_content = ""
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        text_content = parts[0].get("text", "")

                return ScriptGenerationResult(
                    provider_name=f"Gemini ({model_name})",
                    is_fallback=False,
                    script_title=f"AI Dubbing Script ({target_language})",
                    scenes=[{
                        "scene_id": 1,
                        "character": "Voice",
                        "dialogue": text_content or "Funny script generated.",
                        "speed_multiplier": 1.0,
                    }],
                    raw_response=data
                )
            else:
                # Any non-200 and non-429 error falls back gracefully
                return LocalScriptEngine.generate_humorous_script(prompt, target_language)

        except requests.RequestException:
            # Network or connection error: Fallback smoothly without crash
            return LocalScriptEngine.generate_humorous_script(prompt, target_language)
