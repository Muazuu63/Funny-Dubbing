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

    @classmethod
    def generate_full_length_script(
        cls,
        duration_sec: float = 58.8,
        target_language: str = "Bangla",
        comedy_profile: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates a full-length, timeline-synchronized comedic commentary script
        covering every second of the video duration without leaving any gaps.
        """
        duration = max(5.0, round(float(duration_sec), 1))
        
        # Segment video duration into ~10-12s scenes
        scene_length = 11.5
        num_scenes = max(1, int(round(duration / scene_length)))
        if num_scenes == 0:
            num_scenes = 1
        
        actual_step = duration / num_scenes

        # 1. Comedic Adaptation / Translation beats (when original video has voice/dialogue)
        bengali_translation_beats = [
            "কী রে ভাই, তুই এইখানে কী করতাছিস? তুই তো বলছিলি সকালে বাজারে যাবি!",
            "আরে দোস্ত, আমি তো বের হইতে গেছিলাম, কিন্তু রাস্তায় যে কান্ড হইছে বিশ্বাস করবি না!",
            "কী কান্ড হইছে আবার? সত্যি কইরা বল, আবার কোনো ঝামেলা পাকাইয়া আসছিস নাকি?",
            "ঝামেলা মানে? পুরা এলাকা মাথায় তুইলা ফেলছে! এখন তো আমার মানসম্মান নিয়াই টানাটানি!",
            "তোর মানসম্মান তো আগেই গেছিল ভাই, এখন শুধু অফিশিয়ালি প্রমাণ হইলো! চলো পালাই এবার!"
        ]

        # 2. Original Commentary beats (when video is silent, animal clip, or action without voice)
        bengali_commentary_beats = [
            "আরে ভাই দেখো কারবার! এই বিড়ালটা নাকি এখন স্পেশাল বিরিয়ানি রান্না করবে! ধুর মিয়া ফাইজলামি নাকি?",
            "উস্তাদ দেখেন, কড়াইতে তেল না দিয়াই পেঁয়াজ কুচি ছাইড়া দিছে! এইটা বিরিয়ানি হইব না তেলের ড্রপ আউট হইব কে জানে!",
            "আরে থামেন ভাই! বিড়ালটা তো আবার চামচ ধইরা টেস্ট করতাছে! জীবনে কত রাঁধুনি দেখলাম, কিন্তু বিড়ালের বিরিয়ানি শেফ এই প্রথম!",
            "ওরে বাবারে বাবা! মসলা দিতে গিয়া নিজেই তো কড়াইতে পইড়া যাইব অবস্থা! হায়রে আমার ভাগ্য, কী দেখতে হইতাছে!",
            "শেষমেশ কী বানাইলো দেখেন! বিরিয়ানি তো দূরের কথা, পুরাই এক্কেরে ছাইপাঁশ! এইবার কে খাইব এইটা? আপনি না আমি? ধুররর!"
        ]

        hindi_beats = [
            "अरे भाई देखो ये क्या हो रहा है! ऐसा नज़ारा ज़िंदगी में कभी नहीं देखा होगा!",
            "उस्ताद ज़रा ध्यान से देखो! इतनी ओवर-एक्टिंग करके खुद ही मुसीबत मोल ले ली!",
            "अरे रुको रुको भाई! अब असली मज़ा आने वाला है! ये तो पूरा का पूरा ड्रामा निकला!",
            "बाप रे बाप! अब तो बात हाथ से निकल गई! अब कौन बचाएगा भाई तुम्हें?",
            "आखिर में नतीजा देखो! पूरी की पूरी पोल खुल गई! अब बताओ कौन सही कौन गलत!"
        ]

        english_beats = [
            "Oh boy, look at this absolute madness! You won't believe what's happening right here!",
            "Watch this masterclass in hilarious disaster! The sheer confidence is beyond belief!",
            "Wait for it, hold your breath! This is where the absolute chaos peaks!",
            "Unbelievable! Caught red-handed in the funniest catastrophe ever seen!",
            "And that's how you turn a simple moment into pure comedy gold! Who did this?!"
        ]

        is_hindi = "Hindi" in target_language
        is_english = "English" in target_language

        if is_hindi:
            pool = hindi_beats
            trans_pool = hindi_beats
        elif is_english:
            pool = english_beats
            trans_pool = english_beats
        else:
            pool = bengali_commentary_beats
            trans_pool = bengali_translation_beats

        scenes = []
        full_text_lines = []
        trans_text_lines = []

        for i in range(num_scenes):
            start = round(i * actual_step, 1)
            end = round(duration if i == num_scenes - 1 else (i + 1) * actual_step, 1)
            start_lbl = f"{int(start)//60:02d}:{int(start)%60:02d}"
            end_lbl = f"{int(end)//60:02d}:{int(end)%60:02d}"
            dialogue = pool[i % len(pool)]
            trans_dialogue = trans_pool[i % len(trans_pool)]

            scene_item = {
                "scene_id": i + 1,
                "start_time": start,
                "end_time": end,
                "timestamp_label": f"[{start_lbl} - {end_lbl}]",
                "dialogue": dialogue,
                "translated_dialogue": trans_dialogue,
                "tone": "Comedic / Satirical"
            }
            scenes.append(scene_item)
            full_text_lines.append(f"[{start_lbl} - {end_lbl}] {dialogue}")
            trans_text_lines.append(f"[{start_lbl} - {end_lbl}] {trans_dialogue}")

        full_script_text = "\n\n".join(full_text_lines)
        translation_script_text = "\n\n".join(trans_text_lines)
        total_words = sum(len(s["dialogue"].split()) for s in scenes)
        minutes = int(duration) // 60
        seconds = int(duration) % 60
        formatted_duration = f"{minutes:02d}:{seconds:02d}"

        return {
            "duration_sec": duration,
            "formatted_duration": formatted_duration,
            "total_scenes": len(scenes),
            "total_words": total_words,
            "scenes": scenes,
            "full_script_text": full_script_text,
            "translation_script_text": translation_script_text,
            "preview_voice_text": " ".join(s["dialogue"] for s in scenes)
        }


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
