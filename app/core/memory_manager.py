"""
Memory and Resource Manager for AI-VPS.
Master Architecture v2.2 & PRD v2.2 Aligned.

Enforces:
1. Strict resource readiness gates prior to launching heavy worker processes.
2. Accurate RAM/VRAM telemetry via psutil (without unrealistic 100% cleanup claims).
3. ResourceExhaustionError on low system memory (OOM avoidance).
4. Sequential engine loading/unloading discipline.
"""
import gc
import psutil
from typing import Dict, Any, Optional


class ResourceExhaustionError(Exception):
    """Raised when host memory is insufficient to safely launch or continue task execution (OOM avoidance)."""
    pass


class MemoryManager:
    def __init__(self, min_free_ram_gb_buffer: float = 0.1):
        self.min_free_ram_gb_buffer = min_free_ram_gb_buffer
        self._current_loaded_engine: Optional[str] = None

    def get_system_memory(self) -> Dict[str, float]:
        """Returns host RAM metrics in Gigabytes."""
        mem = psutil.virtual_memory()
        return {
            "total_gb": round(mem.total / (1024 ** 3), 2),
            "available_gb": round(mem.available / (1024 ** 3), 2),
            "used_gb": round(mem.used / (1024 ** 3), 2),
            "percent_used": mem.percent,
        }

    def check_resource_readiness(self, required_ram_gb: float) -> bool:
        """
        Step 1 & Step 9 Readiness Gate:
        Checks if available RAM meets requirement plus safe buffer.
        Raises ResourceExhaustionError if memory is below safety threshold.
        """
        mem = psutil.virtual_memory()
        available_gb = mem.available / (1024 ** 3)
        effective_required = required_ram_gb + self.min_free_ram_gb_buffer

        if available_gb < effective_required:
            raise ResourceExhaustionError(
                f"Memory Exhaustion: Available RAM is {available_gb:.2f} GB, but "
                f"task requires {required_ram_gb:.2f} GB (plus {self.min_free_ram_gb_buffer:.2f} GB buffer). "
                f"Task aborted to prevent OS Out-Of-Memory freeze."
            )
        return True

    def release_memory(self) -> Dict[str, float]:
        """
        Step 8: Sequential memory cleanup.
        Forces Python garbage collection.
        Note: Operating System and GPU drivers manage low-level page releases;
        this method does not guarantee 100% instantaneous OS memory reclaim.
        """
        gc.collect()
        
        # If torch happens to be in subprocess or local env, clear cuda cache safely
        try:
            import sys
            if "torch" in sys.modules:
                torch = sys.modules["torch"]
                if hasattr(torch, "cuda") and torch.cuda.is_available():
                    torch.cuda.empty_cache()
        except Exception:
            pass

        return self.get_system_memory()

    def set_current_engine(self, engine_name: Optional[str]) -> None:
        self._current_loaded_engine = engine_name

    def get_current_engine(self) -> Optional[str]:
        return self._current_loaded_engine


memory_manager = MemoryManager()
