"""Lip-sync engine interface (Wav2Lip optional engine wrapper)."""

class LipSyncEngine:
    def __init__(self):
        self.name = "Wav2Lip"

    def is_available(self) -> bool:
        return False
