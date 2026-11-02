"""
Pydantic Schemas and TypeScript-compatible Data Models for AI-VPS.
Master Architecture v2.2 & PRD v2.2 Aligned.
Supports camelCase <-> snake_case automatic mapping via ConfigDict(populate_by_name=True).
"""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum
from app.config import (
    OutputLanguage,
    CommercialUseStatus,
    CheckpointCommitState,
    TaskLifecycleState,
)


class ScriptApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ModelVerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    MANUAL_CONFIRMED = "MANUAL_CONFIRMED"


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        use_enum_values=True
    )


# ==========================================
# 1. Project Models
# ==========================================
class ProjectBase(BaseSchema):
    title: str = Field(..., description="Project Title")
    mode: str = Field(..., description="Operating Mode ID (e.g. mode01_dubbing)")
    input_video_path: Optional[str] = Field(None, alias="inputVideoPath")
    target_languages: List[str] = Field(default_factory=lambda: ["Bangla"], alias="targetLanguages")
    status: str = Field(default="CREATED")


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: str
    created_at: str = Field(..., alias="createdAt")
    updated_at: str = Field(..., alias="updatedAt")


# ==========================================
# 2. Task Manifest Models (Dual Durability)
# ==========================================
class TaskManifestBase(BaseSchema):
    project_id: str = Field(..., alias="projectId")
    step_name: str = Field(..., alias="stepName")
    status: str = Field(default="INTENT")
    sidecar_path: Optional[str] = Field(None, alias="sidecarPath")
    staging_path: Optional[str] = Field(None, alias="stagingPath")
    final_output_path: Optional[str] = Field(None, alias="finalOutputPath")
    expected_format: Optional[str] = Field(None, alias="expectedFormat")
    file_size_bytes: int = Field(default=0, alias="fileSizeBytes")
    sha256_checksum: Optional[str] = Field(None, alias="sha256Checksum")
    recovery_metadata_json: Optional[str] = Field(default="{}", alias="recoveryMetadataJson")


class TaskManifestCreate(TaskManifestBase):
    task_id: str = Field(..., alias="taskId")


class TaskManifest(TaskManifestBase):
    task_id: str = Field(..., alias="taskId")
    updated_at: str = Field(..., alias="updatedAt")


# ==========================================
# 3. Script Models
# ==========================================
class ScriptBase(BaseSchema):
    project_id: str = Field(..., alias="projectId")
    script_title: str = Field(..., alias="scriptTitle")
    scenes_json: Union[str, List[Dict[str, Any]]] = Field(..., alias="scenesJson")
    selected_flag: bool = Field(default=False, alias="selectedFlag")
    approval_status: ScriptApprovalStatus = Field(default=ScriptApprovalStatus.PENDING, alias="approvalStatus")


class ScriptCreate(ScriptBase):
    pass


class Script(ScriptBase):
    id: str
    created_at: str = Field(..., alias="createdAt")
    updated_at: str = Field(..., alias="updatedAt")


# ==========================================
# 4. Audio Mixer State Models (TypeScript Mapping)
# ==========================================
class AudioMixerStateBase(BaseSchema):
    original_audio_volume: float = Field(default=1.0, ge=0.0, le=1.5, alias="originalAudioVolume")
    original_audio_muted: bool = Field(default=True, alias="originalAudioMuted")
    demucs_vocal_volume: float = Field(default=1.0, ge=0.0, le=1.5, alias="demucsVocalVolume")
    demucs_accompaniment_volume: float = Field(default=1.0, ge=0.0, le=1.5, alias="demucsAccompanimentVolume")
    ai_voice_volume: float = Field(default=1.0, ge=0.0, le=1.5, alias="aiVoiceVolume")
    master_volume: float = Field(default=1.0, ge=0.0, le=1.5, alias="masterVolume")
    
    # Dual alias support for TypeScript: masterLevelDb and masterLevelDbfs
    master_level_dbfs: float = Field(
        default=-60.0,
        ge=-60.0,
        le=6.0,
        alias="masterLevelDbfs",
        validation_alias="masterLevelDb"
    )
    peak_clipping_detected: bool = Field(default=False, alias="peakClippingDetected")
    hard_limiter_enabled: bool = Field(default=True, alias="hardLimiterEnabled")
    normalizer_enabled: bool = Field(default=True, alias="normalizerEnabled")
    normalizer_target_lufs: float = Field(default=-16.0, ge=-24.0, le=-12.0, alias="normalizerTargetLufs")


class AudioMixerStateCreate(AudioMixerStateBase):
    project_id: str = Field(..., alias="projectId")


class AudioMixerState(AudioMixerStateBase):
    id: str
    project_id: str = Field(..., alias="projectId")
    updated_at: str = Field(..., alias="updatedAt")


# ==========================================
# 5. System Settings Models
# ==========================================
class SystemSettingsBase(BaseSchema):
    verified_free_models: Union[str, List[str]] = Field(default_factory=list, alias="verifiedFreeModels")
    active_gemini_model: str = Field(default="gemini-1.5-flash", alias="activeGeminiModel")
    offline_mode_enabled: bool = Field(default=False, alias="offlineModeEnabled")
    commercial_mode_strict: bool = Field(default=True, alias="commercialModeStrict")


class SystemSettings(SystemSettingsBase):
    id: str = "default"
    updated_at: str = Field(..., alias="updatedAt")


# ==========================================
# 6. Model Commercial License Registry (27 Fields)
# ==========================================
class ModelRegistryBase(BaseSchema):
    # 1. model_id
    model_id: str = Field(..., alias="modelId", description="Unique Model ID or Slug")
    # 2. name
    name: str = Field(..., description="Display Name")
    # 3. task_type
    task_type: str = Field(..., alias="taskType", description="separation, stt, tts, inpaint, lipsync")
    # 4. engine_type
    engine_type: str = Field(..., alias="engineType", description="local_offline, cloud_free, cloud_hybrid")
    # 5. version
    version: str = Field(default="1.0.0", description="Model release version")
    # 6. weights_source
    weights_source: str = Field(..., alias="weightsSource", description="HuggingFace, Local, etc.")
    # 7. code_license
    code_license: str = Field(..., alias="codeLicense", description="MIT, Apache-2.0, BSD, etc.")
    # 8. weights_license
    weights_license: str = Field(..., alias="weightsLicense", description="OpenRAIL, CC-BY-NC, etc.")
    # 9. dataset_license
    dataset_license: str = Field(..., alias="datasetLicense", description="Dataset licensing terms")
    # 10. voice_asset_license
    voice_asset_license: str = Field(..., alias="voiceAssetLicense", description="Voice licensing terms")
    # 11. exact_license_version
    exact_license_version: str = Field(..., alias="exactLicenseVersion", description="e.g. 2.0, 3.0")
    # 12. official_license_url
    official_license_url: str = Field(..., alias="officialLicenseUrl", description="Official license URL")
    # 13. official_download_url
    official_download_url: str = Field(..., alias="officialDownloadUrl", description="Official weights download URL")
    # 14. commercial_use_status
    commercial_use_status: CommercialUseStatus = Field(
        default=CommercialUseStatus.ALLOWED,
        alias="commercialUseStatus",
        description="ALLOWED, FORBIDDEN, UNCERTAIN"
    )
    # 15. attribution_required
    attribution_required: bool = Field(default=False, alias="attributionRequired")
    # 16. attribution_text
    attribution_text: Optional[str] = Field(None, alias="attributionText")
    # 17. verification_evidence
    verification_evidence: str = Field(..., alias="verificationEvidence", description="Audit note/evidence")
    # 18. checksum_sha256
    checksum_sha256: str = Field(..., alias="checksumSha256", description="SHA-256 Checksum")
    # 19. local_path
    local_path: str = Field(..., alias="localPath", description="Relative path in storage/models")
    # 20. min_ram_gb
    min_ram_gb: float = Field(default=4.0, ge=1.0, alias="minRamGb")
    # 21. min_vram_gb
    min_vram_gb: float = Field(default=0.0, ge=0.0, alias="minVramGb")
    # 22. recommended_device
    recommended_device: str = Field(default="cpu", alias="recommendedDevice")
    # 23. cpu_support
    cpu_support: bool = Field(default=True, alias="cpuSupport")
    # 24. offline_capable
    offline_capable: bool = Field(default=True, alias="offlineCapable")
    # 25. internet_requirement
    internet_requirement: bool = Field(default=False, alias="internetRequirement")
    # 26. verification_status
    verification_status: ModelVerificationStatus = Field(
        default=ModelVerificationStatus.UNVERIFIED,
        alias="verificationStatus"
    )
    # 27. last_verified_date
    last_verified_date: str = Field(..., alias="lastVerifiedDate", description="ISO Date string")


class ModelRegistryCreate(ModelRegistryBase):
    pass


class ModelRegistry(ModelRegistryBase):
    pass
