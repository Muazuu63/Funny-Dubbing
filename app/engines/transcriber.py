"""Speech-to-text transcription engine interface (Whisper optional engine wrapper)."""

class TranscriberEngine:
    def __init__(self):
        self.name = "Whisper"

    def is_available(self) -> bool:
        try:
            import whisper
            return True
        except ImportError:
            return False
