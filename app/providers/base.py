"""Base provider abstract classes."""
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_script(self, prompt: str, **kwargs) -> Dict[str, Any]:
        pass

class BaseTTSProvider(ABC):
    @abstractmethod
    async def synthesize(self, text: str, output_path: str, **kwargs) -> str:
        pass
