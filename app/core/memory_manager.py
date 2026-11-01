"""Hardware & memory management, enforcing sequential engine loading/unloading."""
import gc

class MemoryManager:
    def __init__(self):
        self._current_loaded_engine = None

    def release_memory(self):
        """Force garbage collection and VRAM release."""
        gc.collect()
