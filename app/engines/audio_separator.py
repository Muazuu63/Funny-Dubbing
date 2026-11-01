"""Audio separation engine interface (Demucs optional engine wrapper)."""
from pathlib import Path

class AudioSeparatorEngine:
    def __init__(self):
        self.name = "Demucs"

    def is_available(self) -> bool:
        try:
            import demucs
            return True
        except ImportError:
            return False
