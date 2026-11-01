"""Security validators: path traversal protection and MIME allowlisting."""
from pathlib import Path
from app.config import settings

def validate_safe_path(target_path: Path, base_dir: Path) -> Path:
    resolved_target = target_path.resolve()
    resolved_base = base_dir.resolve()
    if not str(resolved_target).startswith(str(resolved_base)):
        raise ValueError(f"Path traversal detected: {target_path} is outside {base_dir}")
    return resolved_target
