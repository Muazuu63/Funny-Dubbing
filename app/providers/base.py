"""
Base Provider Interfaces for AI-VPS.
Master Architecture v2.2 & PRD v2.2 Aligned.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.config import GeminiVerificationStatus


class PrivacyConsentData(BaseModel):
    user_consent_granted: bool = False
    consent_timestamp: Optional[str] = None
    api_key_fingerprint: Optional[str] = None
    data_types_shared: List[str] = Field(default_factory=list)  # e.g. ["Text", "Frames", "Audio", "Transcription"]


class QuadCheckResult(BaseModel):
    status: GeminiVerificationStatus
    model_availability: bool = False
    free_tier_eligibility: str = "UNKNOWN"
    billing_configuration: str = "UNKNOWN"
    remaining_quota: str = "UNKNOWN"
    details: str = ""


class ScriptGenerationResult(BaseModel):
    provider_name: str
    is_fallback: bool = False
    script_title: str
    scenes: List[Dict[str, Any]]
    raw_response: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class BaseLLMProvider(ABC):
    @abstractmethod
    async def quad_check(self, model_name: str) -> QuadCheckResult:
        """Perform 4-point capability & free-tier eligibility check."""
        pass

    @abstractmethod
    async def generate_script(
        self,
        prompt: str,
        target_language: str = "Bangla",
        privacy_consent: Optional[PrivacyConsentData] = None,
        **kwargs
    ) -> ScriptGenerationResult:
        """Generate humorous dubbing script with fallback fail-safe."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is online, configured and permitted."""
        pass


class BaseTTSProvider(ABC):
    @abstractmethod
    async def synthesize(
        self,
        text: str,
        output_path: str,
        voice_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """Synthesize text to audio speech file."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if engine is available and permitted."""
        pass
