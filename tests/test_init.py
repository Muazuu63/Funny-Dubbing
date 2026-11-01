"""Phase 1 initialization test verifying directory setup, settings, single-port lock, and binary resolution."""
import pytest
from pathlib import Path
from app.config import settings, SupportedLanguage

def test_directories_exist():
    """Verify that all core directories are created."""
    assert settings.STORAGE_DIR.exists()
    assert settings.PROJECTS_DIR.exists()
    assert settings.MODELS_DIR.exists()
    assert settings.TRAINING_DIR.exists()
    assert settings.BIN_DIR.exists()

def test_network_binding_and_single_port():
    """Verify strictly single-port architecture: 127.0.0.1:8000."""
    assert settings.HOST == "127.0.0.1"
    assert settings.PORT == 8000
    assert str(settings.PORT) == "8000"

def test_strict_language_matrix():
    """Verify the 5 exact Title-Cased language matrix strings."""
    expected_languages = [
        "Bangla",
        "Hindi",
        "English",
        "Bangla + Hindi",
        "Bangla + Hindi + English",
    ]
    actual_languages = [lang.value for lang in SupportedLanguage]
    assert actual_languages == expected_languages
    assert len(SupportedLanguage) == 5

def test_ffmpeg_binary_resolution():
    """Verify binary resolver inspects ./bin/ first."""
    # Ensure bin dir is checked
    bin_ffmpeg = settings.BIN_DIR / ("ffmpeg.exe" if settings.is_windows() else "ffmpeg")
    resolved = settings.resolve_ffmpeg_binary()
    if bin_ffmpeg.exists():
        assert str(resolved) == str(bin_ffmpeg.resolve()) or resolved == bin_ffmpeg
    else:
        # Either found in PATH or defaults to ffmpeg
        assert resolved is not None
        assert "ffmpeg" in str(resolved).lower()

def test_security_allowlists():
    """Verify MIME and file extensions security allowlists."""
    assert "video/mp4" in settings.ALLOWED_MIME_TYPES
    assert "audio/wav" in settings.ALLOWED_MIME_TYPES
    assert ".mp4" in settings.ALLOWED_EXTENSIONS
    assert ".wav" in settings.ALLOWED_EXTENSIONS
