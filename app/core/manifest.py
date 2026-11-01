"""Durable task manifest writer and reader."""
import json
from pathlib import Path

class TaskManifestManager:
    @staticmethod
    def write_manifest(manifest_path: Path, manifest_data: dict) -> None:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)
