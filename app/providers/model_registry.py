"""Registry for dynamically discovering and loading AI model weights and engines."""
from typing import Dict, Any

class ModelRegistry:
    def __init__(self):
        self._registry: Dict[str, Any] = {}

    def register(self, model_id: str, model_info: dict):
        self._registry[model_id] = model_info

    def get(self, model_id: str):
        return self._registry.get(model_id)

model_registry = ModelRegistry()
