"""
AI-VPS Configuration Module
Master System Architecture v2.2 & PRD v2.2 Aligned.
"""

from enum import Enum
from pathlib import Path
import os
import shutil
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OutputLanguage(str, Enum):
    BANGLA = "Bangla"
    HINDI = "Hindi"
    ENGLISH = "English"
    BANGLA_HINDI = "Bangla + Hindi"
    BANGLA_HINDI_ENGLISH = "Bangla + Hindi + English"


# Alias for backward compatibility
SupportedLanguage = OutputLanguage


class GeminiVerificationStatus(str, Enum):
    VERIFIED_FREE = "VERIFIED_FREE"
    MANUAL_CONFIRMATION = "MANUAL_CONFIRMATION"
    UNAVAILABLE = "UNAVAILABLE"


class EngineStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    INSTALL_REQUIRED = "INSTALL_REQUIRED"
    VERIFICATION_REQUIRED = "VERIFICATION_REQUIRED"


class CommercialUseStatus(str, Enum):
    ALLOWED = "ALLOWED"
    FORBIDDEN = "FORBIDDEN"
    UNCERTAIN = "UNCERTAIN"


class CheckpointCommitState(str, Enum):
    INTENT = "INTENT"
    RENDERING = "RENDERING"
    VALIDATED = "VALIDATED"
    OUTPUT_COMMITTED = "OUTPUT_COMMITTED"
    DB_COMMITTED = "DB_COMMITTED"


class TaskLifecycleState(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    RECOVERY_REQUIRED = "RECOVERY_REQUIRED"


class Settings(BaseSettings):
    """
    Central Application Settings
    Single fixed port: 127.0.0.1:8000
    Relative paths from project root.
    """
    model_config = SettingsConfigDict(
        env_prefix="AIVPS_",
        env_file=".env",
        extra="ignore"
    )

    # Server Binding
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    @property
    def BASE_URL(self) -> str:
        return f"http://{self.HOST}:{self.PORT}"

    # Paths (Relative to Project Root)
    BASE_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent)

    @property
    def STORAGE_DIR(self) -> Path:
        return self.BASE_DIR / "storage"

    @property
    def DATABASE_PATH(self) -> Path:
        return self.STORAGE_DIR / "studio.db"

    @property
    def MODELS_DIR(self) -> Path:
        return self.STORAGE_DIR / "models"

    @property
    def PROJECTS_DIR(self) -> Path:
        return self.STORAGE_DIR / "projects"

    @property
    def TRAINING_PROFILES_DIR(self) -> Path:
        return self.STORAGE_DIR / "training_profiles"

    @property
    def TRAINING_DIR(self) -> Path:
        return self.TRAINING_PROFILES_DIR

    @staticmethod
    def is_windows() -> bool:
        return os.name == "nt"

    ALLOWED_MIME_TYPES: List[str] = [
        "video/mp4",
        "video/quicktime",
        "video/x-matroska",
        "audio/wav",
        "audio/mpeg",
        "audio/mp3",
        "image/png",
        "image/jpeg",
    ]

    ALLOWED_EXTENSIONS: List[str] = [
        ".mp4",
        ".mov",
        ".mkv",
        ".wav",
        ".mp3",
        ".png",
        ".jpg",
        ".jpeg",
    ]

    @property
    def BIN_DIR(self) -> Path:
        return self.BASE_DIR / "bin"

    @property
    def FRONTEND_DIST_DIR(self) -> Path:
        return self.BASE_DIR / "frontend" / "dist"

    # Security Allowlist
    ALLOWED_HOSTS: List[str] = [
        "127.0.0.1:8000",
        "localhost:8000",
        "127.0.0.1",
        "localhost"
    ]
    
    TRUSTED_ORIGINS: List[str] = [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "tauri://localhost",
        "http://tauri.localhost"
    ]

    # Offline Mode Flag
    OFFLINE_MODE_ENABLED: bool = False

    # Audio Mixer Safety Defaults
    DEFAULT_TRACK_VOLUME: float = 1.0
    DEFAULT_MASTER_VOLUME: float = 1.0
    LIMITER_CEILING_DBFS: float = -0.5
    NORMALIZER_TARGET_LUFS: float = -16.0
    CLIPPING_THRESHOLD_DBFS: float = 0.0

    # Worker Queue Defaults
    WORKER_TIMEOUT_SEC: int = 600
    WORKER_MAX_RETRY_COUNT: int = 2

    def resolve_ffmpeg_binary(self) -> Path:
        """
        Resolves FFmpeg executable path:
        1. Checks project local bin directory: ./bin/ffmpeg.exe
        2. Falls back to system PATH
        """
        local_binary = self.BIN_DIR / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
        if local_binary.is_file() and os.access(local_binary, os.X_OK):
            return local_binary

        system_bin = shutil.which("ffmpeg")
        if system_bin:
            return Path(system_bin)

        # Fallback to anticipated local path
        return local_binary

    def resolve_ffprobe_binary(self) -> Path:
        """
        Resolves FFprobe executable path:
        1. Checks project local bin directory: ./bin/ffprobe.exe
        2. Falls back to system PATH
        """
        local_binary = self.BIN_DIR / ("ffprobe.exe" if os.name == "nt" else "ffprobe")
        if local_binary.is_file() and os.access(local_binary, os.X_OK):
            return local_binary

        system_bin = shutil.which("ffprobe")
        if system_bin:
            return Path(system_bin)

        return local_binary

    def ensure_directories(self) -> None:
        """Creates storage and workspace directories if not present."""
        self.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        self.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        self.PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
        self.TRAINING_PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        self.BIN_DIR.mkdir(parents=True, exist_ok=True)


# Global Settings Instance
settings = Settings()
