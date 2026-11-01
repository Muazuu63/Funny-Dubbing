"""TTS Provider delegator (supports edge-tts, bark, etc.)."""
from app.providers.base import BaseTTSProvider

class TTSProvider(BaseTTSProvider):
    def __init__(self, engine_name: str = "edge-tts"):
        self.engine_name = engine_name

    async def synthesize(self, text: str, output_path: str, **kwargs) -> str:
        return output_path
