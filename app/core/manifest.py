"""
Durable Task Manifest Manager for AI-VPS.
Master Architecture v2.2 & PRD v2.2 Aligned.

Guarantees:
1. Atomic Sidecar Write: (.tmp -> flush -> fsync -> close -> os.replace).
2. Robust parsing with corruption detection.
3. Strict Path Traversal containment within project directory.
"""
import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from app.core.security import validate_safe_path

logger = logging.getLogger("ai_vps.manifest")


class ManifestCorruptedError(Exception):
    """Raised when sidecar manifest JSON is malformed or unreadable."""
    pass


class TaskManifestManager:
    @staticmethod
    def write_manifest_atomic(manifest_path: Path, manifest_data: dict, project_dir: Optional[Path] = None) -> None:
        """
        Durable atomic write:
        Writes to .tmp, flushes OS buffer, calls fsync, closes, and atomically renames.
        """
        if project_dir:
            validate_safe_path(manifest_path, project_dir)

        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = manifest_path.with_suffix(manifest_path.suffix + ".tmp")

        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(manifest_data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())

            # Atomic replace (Windows safe)
            os.replace(tmp_path, manifest_path)
        except Exception as e:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except Exception:
                    pass
            raise IOError(f"Failed to atomically write manifest to {manifest_path}: {e}") from e

    @staticmethod
    def read_manifest(manifest_path: Path, project_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        Reads and parses JSON manifest. Raises ManifestCorruptedError if malformed.
        """
        if project_dir:
            validate_safe_path(manifest_path, project_dir)

        if not manifest_path.is_file():
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as err:
            raise ManifestCorruptedError(f"Corrupted sidecar manifest at {manifest_path}: {err}") from err
