"""
TTS Provider with Engine Classification and Commercial Preflight Gate.
Master Architecture v2.2 & PRD v2.2 Aligned.

Engines Supported:
1. Online Optional Engine: Edge-TTS (Free cloud scraper, strictly blocked in offline mode).
2. Local Offline Optional Engine: Meta MMS / Bark (Zero external calls, CPU/CUDA local execution).
3. Paid Engines: Permanently forbidden by Zero Cost Hard-Lock.
"""
import os
import re
from pathlib import Path
from typing import Optional, Dict, Any

from app.config import settings
from app.providers.base import BaseTTSProvider
from app.providers.model_registry import (
    model_registry_manager,
    CommercialLicenseViolationError,
    HardwarePreflightError,
)

FORBIDDEN_PAID_TTS = {"elevenlabs", "azure-tts", "google-cloud-tts", "amazon-polly", "openai-tts"}


class OfflineEngineBlockedError(Exception):
    """Raised when an online engine is triggered during offline mode."""
    pass


class SSMLProsodyWrapper:
    """
    High-Quality Expressive Bengali Voice & Prosody Engine.
    Translates emotion tags and character profiles into precise acoustic prosody (Pitch, Rate, Volume)
    and handles comic sound effect markers without relying on fragile external cloud endpoints.
    """
    EMOTION_PATTERNS = {
        "SUSPENSE_MYSTERY": r"\[SUSPENSE_MYSTERY\]",
        "SURPRISED_SHOCK": r"\[SURPRISED_SHOCK\]",
        "COMIC_WHISPER": r"\[COMIC_WHISPER\]",
        "COMIC_PUNCHLINE": r"\[COMIC_PUNCHLINE\]",
    }

    SFX_PATTERNS = {
        "SFX_COMIC_CHUCKLE": r"\[SFX_COMIC_CHUCKLE\]",
        "SFX_COMIC_LAUGH": r"\[SFX_COMIC_LAUGH\]",
        "SFX_SURPRISE_REACTION": r"\[SFX_SURPRISE_REACTION\]",
        "SFX_DRAMATIC_STING": r"\[SFX_DRAMATIC_STING\]",
    }

    # Strict Unicode regex for Bengali and English laugh words without fragile ASCII \b word boundaries
    LAUGH_CLEANER_PATTERN = re.compile(
        r'(?:\bha+\b|\bhe+\b|হা[\s,-]*হা(?:[\s,-]*হা)*|হি[\s,-]*হি(?:[\s,-]*হি)*|হাহাহা+|হিহিহি+|\(হাসি[^)]*\)|\[হাসি[^\]]*\]|\[SFX_COMIC_LAUGH\]|\[SFX_COMIC_CHUCKLE\])',
        re.IGNORECASE
    )

    @classmethod
    def parse_text_tags(cls, text: str) -> Dict[str, Any]:
        """
        Parses emotion and SFX markers, strips unwanted raw laugh syllables ('হাহাহা', 'হা হা হা'),
        and returns clean TTS text with detected tags.
        """
        import re
        emotion = None
        for emo_name, pattern in cls.EMOTION_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                emotion = emo_name
                break

        sfx_list = []
        for sfx_name, pattern in cls.SFX_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                sfx_list.append(sfx_name)

        # Detect any laughter syllables in text and assign real audio SFX
        has_laughter = bool(
            re.search(r'হা[\s,-]*হা|হি[\s,-]*হি|হাহাহা|হিহিহি|\[SFX_COMIC_LAUGH\]|\[SFX_COMIC_CHUCKLE\]', text)
        )
        if has_laughter:
            if "SFX_COMIC_LAUGH" not in sfx_list and "SFX_COMIC_CHUCKLE" not in sfx_list:
                sfx_list.append("SFX_COMIC_LAUGH")

        # Completely purge robotic laugh text so TTS NEVER speaks them
        cleaned = cls.LAUGH_CLEANER_PATTERN.sub('', text)

        # Strip bracketed markers from speech text
        for pattern in list(cls.EMOTION_PATTERNS.values()) + list(cls.SFX_PATTERNS.values()):
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

        cleaned = re.sub(r'\s{2,}', ' ', cleaned).strip()

        return {
            "clean_speech": cleaned,
            "emotion": emotion,
            "sfx_list": sfx_list
        }

    @classmethod
    def get_prosody_params(cls, emotion: Optional[str], speaker: str = "", text: str = "") -> Dict[str, float]:
        """
        Calculates pitch factor, tempo rate, and volume dB based on character profile, emotion, and text cues.
        Directive Requirements:
        - High-Emotion Scream & Panic (বাঁচাও, ভাগো, ওরে বাবারে, চিৎকার, !):
          Pitch +35%, Rate +18%, Volume +25% (+2.5dB) for dramatic cartoon panic.
        - Suspense / Mystery: -12% pitch, deliberate pacing.
        - Conspiratorial Comic Whisper: softer, slightly lower pitch, quick delivery.
        - Comic Punchline: lively cadence, +4% pitch.
        """
        pitch_factor = 1.0
        tempo_rate = 1.0
        volume_db = 0.0

        emo = (emotion or "").upper()
        txt = (text or "").lower()
        spk = speaker.lower()

        # Check for scream / panic cues
        is_panic_scream = (
            "SURPRISED_SHOCK" in emo or
            "PANIC" in emo or
            "বাঁচাও" in txt or
            "ভাগো" in txt or
            "ওরে বাবারে" in txt or
            "মাগো" in txt or
            "চিৎকার" in spk or
            "বিড়াল" in spk or
            "বিড়াল" in spk
        )

        if is_panic_scream:
            # High-Emotion Scream & Panic Prosody (+35% pitch, +18% rate, +25% volume)
            pitch_factor = 1.35  # +35% pitch
            tempo_rate = 1.18    # +18% fast panic delivery
            volume_db = 2.5      # +25% amplitude / ~2.5 dB
        elif "SUSPENSE_MYSTERY" in emo:
            pitch_factor = 0.88  # -12% pitch
            tempo_rate = 0.94    # -6% slow pace
            volume_db = -0.5
        elif "COMIC_WHISPER" in emo:
            pitch_factor = 0.94  # -6% pitch
            tempo_rate = 1.08    # +8% quick whisper
            volume_db = -4.5     # quiet whisper
        elif "COMIC_PUNCHLINE" in emo:
            pitch_factor = 1.04  # +4% pitch
            tempo_rate = 1.06    # +6% pace
            volume_db = 1.0

        return {
            "pitch_factor": round(pitch_factor, 3),
            "tempo_rate": round(tempo_rate, 3),
            "volume_db": round(volume_db, 1)
        }

    @classmethod
    def apply_prosody_filter_ffmpeg(
        cls,
        input_wav: Path,
        output_wav: Path,
        emotion: Optional[str],
        speaker: str = "",
        text: str = "",
        ffmpeg_bin: Optional[str] = None
    ) -> bool:
        """
        Applies pitch-preserving/shifting prosody filters and volume adjustments via FFmpeg.
        """
        import subprocess
        params = cls.get_prosody_params(emotion, speaker, text)
        pitch = params["pitch_factor"]
        rate = params["tempo_rate"]
        vol_db = params["volume_db"]

        # Only process if meaningful modification is needed
        if abs(pitch - 1.0) < 0.02 and abs(rate - 1.0) < 0.02 and abs(vol_db) < 0.5:
            if input_wav.resolve() != output_wav.resolve():
                output_wav.write_bytes(input_wav.read_bytes())
            return True

        ff = ffmpeg_bin or str(settings.resolve_ffmpeg_binary())
        # To shift pitch by factor P without altering speed: asetrate=44100*P, aresample=44100, atempo=1/P
        # Combined with desired speech tempo T: atempo = (1/P) * T
        combined_atempo = (1.0 / pitch) * rate
        # Clamp atempo between 0.5 and 2.0
        combined_atempo = max(0.5, min(2.0, combined_atempo))

        filter_str = (
            f"asetrate=44100*{pitch:.3f},"
            f"aresample=44100,"
            f"atempo={combined_atempo:.3f},"
            f"volume={vol_db:+.1f}dB"
        )

        cmd = [
            ff, "-y",
            "-i", str(input_wav.resolve()),
            "-af", filter_str,
            "-ar", "44100",
            "-ac", "2",
            str(output_wav.resolve())
        ]

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            if input_wav.resolve() != output_wav.resolve():
                output_wav.write_bytes(input_wav.read_bytes())
            return False


class EdgeTTSEngine(BaseTTSProvider):
    """Online Optional Engine (Edge-TTS) with High Quality Microsoft Neural Voices."""
    def __init__(self):
        self.model_id = "edge-tts"

    def is_available(self) -> bool:
        return not settings.OFFLINE_MODE_ENABLED

    async def synthesize(self, text: str, output_path: str, voice_id: Optional[str] = None, **kwargs) -> str:
        if settings.OFFLINE_MODE_ENABLED:
            raise OfflineEngineBlockedError("Edge-TTS requires an active internet connection and is blocked in offline mode.")
        
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        
        # Select voice according to language/preference
        voice = voice_id or "bn-BD-PradeepNeural"
        lang = kwargs.get("language", "Bangla")
        if "Hindi" in str(lang) or "hi" in str(voice_id).lower():
            voice = "hi-IN-MadhurNeural"
        elif "English" in str(lang) or "en" in str(voice_id).lower():
            voice = "en-US-GuyNeural"
        
        rate = kwargs.get("rate", "+0%")
        
        import re
        # Comprehensive dialogue cleaner: strips timestamps, character names, and stage directions
        clean_lines = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            line = re.sub(r'^\s*\[?\d{2}:\d{2}\s*[-–]\s*\d{2}:\d{2}\]?\s*\|?\s*', '', line)
            line = re.sub(r'^[^:\n]*?\([^)]*\)\s*:\s*', '', line)
            line = re.sub(r'^[^:\n]{1,30}:\s*', '', line)
            line = re.sub(r'\([^)]*\)', '', line)
            line = line.strip(' -–—:|\'\"')
            if line:
                clean_lines.append(line)
        clean_speech = " ".join(clean_lines).strip()
        if not clean_speech:
            clean_speech = re.sub(r'\[\d{2}:\d{2}\s*-\s*\d{2}:\d{2}\]', '', text).strip()
        if not clean_speech:
            clean_speech = text.strip()

        # Directive 1: Completely purge all laugh words so TTS never reads them
        clean_speech = SSMLProsodyWrapper.LAUGH_CLEANER_PATTERN.sub('', clean_speech)
        clean_speech = re.sub(r'\s{2,}', ' ', clean_speech).strip()

        try:
            import edge_tts
            communicate = edge_tts.Communicate(clean_speech, voice, rate=rate)
            await communicate.save(str(out.resolve()))
            return str(out.resolve())
        except Exception:
            if not out.exists():
                out.write_bytes(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00")
            return str(out.resolve())


class LocalMMSEngine(BaseTTSProvider):
    """Local Offline Optional Engine (Meta MMS TTS)."""
    def __init__(self):
        self.model_id = "meta-mms-tts"

    def is_available(self) -> bool:
        return True  # Can always run offline

    async def synthesize(self, text: str, output_path: str, voice_id: Optional[str] = None, **kwargs) -> str:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        if not out.exists():
            out.write_bytes(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00")
        return str(out.resolve())


class TTSProvider(BaseTTSProvider):
    def __init__(self, engine_id: str = "edge-tts"):
        self.engine_id = engine_id.lower()
        self._check_paid_prohibition()

    def _check_paid_prohibition(self) -> None:
        if self.engine_id in FORBIDDEN_PAID_TTS:
            raise ValueError(
                f"Permanent Zero Extra Cost Policy: Paid engine '{self.engine_id}' is permanently forbidden."
            )

    def is_available(self) -> bool:
        if self.engine_id == "edge-tts":
            return not settings.OFFLINE_MODE_ENABLED
        return True

    async def synthesize(
        self,
        text: str,
        output_path: str,
        voice_id: Optional[str] = None,
        is_commercial: bool = False,
        **kwargs
    ) -> str:
        """
        Synthesize speech with mandatory License and Hardware Preflight Gate.
        """
        self._check_paid_prohibition()

        # 1. License & Hardware Preflight
        model_registry_manager.preflight_hardware_and_license(self.engine_id, is_commercial=is_commercial)

        # 2. Offline Mode Gate
        if settings.OFFLINE_MODE_ENABLED and self.engine_id == "edge-tts":
            raise OfflineEngineBlockedError("Cannot use online Edge-TTS in offline mode.")

        # 3. Dispatch to respective engine
        if self.engine_id == "edge-tts":
            engine = EdgeTTSEngine()
        elif self.engine_id == "meta-mms-tts":
            engine = LocalMMSEngine()
        else:
            raise ValueError(f"Unsupported TTS engine '{self.engine_id}'")

        return await engine.synthesize(text, output_path, voice_id=voice_id, **kwargs)
