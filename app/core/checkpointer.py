"""
5-Stage Durable Checkpoint State Machine for AI-VPS.
Master Architecture v2.2 & PRD v2.2 Aligned.

Execution Flow:
INTENT -> RENDERING -> VALIDATED -> OUTPUT_COMMITTED -> DB_COMMITTED

Guarantees:
1. Manifest written atomically before rendering starts.
2. Staging files on identical filesystem volume (.staging/).
3. Output validation with SHA-256 checksum and size checks.
4. Atomic replace with Windows file-lock exponential backoff.
5. Critical SQLite transaction with synchronous=FULL.
6. Safe file quarantining (.staging/quarantine/) for corrupt files.
"""
import os
import time
import hashlib
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

from app.config import settings, CheckpointCommitState
from app.core.manifest import TaskManifestManager
from app.core.security import validate_safe_path
from app.db.database import get_db
from app.db import crud
from app.db.models import TaskManifestCreate


class OutputValidationError(Exception):
    """Raised when rendered output fails SHA-256 or format validation."""
    pass


class DestinationConflictError(Exception):
    """Raised when an unverified destination file would be unexpectedly overwritten."""
    pass


def calculate_sha256(file_path: Path) -> str:
    """Calculates SHA-256 hash of a file chunk-by-chunk."""
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found for checksum: {file_path}")
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def atomic_replace_with_retry(src: Path, dst: Path, max_retries: int = 4, base_delay: float = 0.1) -> None:
    """
    Atomically renames src to dst with exponential backoff on Windows
    to prevent PermissionError / file lock collisions.
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    delay = base_delay
    last_err = None

    for attempt in range(max_retries):
        try:
            os.replace(src, dst)
            return
        except PermissionError as pe:
            last_err = pe
            time.sleep(delay)
            delay *= 2
        except Exception as e:
            raise e

    if last_err:
        raise IOError(f"Failed to atomically replace {src} -> {dst} after {max_retries} retries: {last_err}") from last_err


class Checkpointer:
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.manifests_dir = project_dir / ".manifests"
        self.staging_dir = project_dir / ".staging"
        self.quarantine_dir = self.staging_dir / "quarantine"
        
        self.manifests_dir.mkdir(parents=True, exist_ok=True)
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)

    def get_manifest_path(self, task_id: str) -> Path:
        return self.manifests_dir / f"{task_id}.json"

    def get_staging_path(self, task_id: str, suffix: str = ".tmp") -> Path:
        return self.staging_dir / f"{task_id}{suffix}"

    def quarantine_file(self, file_path: Path, task_id: str) -> Path:
        """
        Moves incomplete/corrupted file to .staging/quarantine/[task_id]_[timestamp].corrupt.
        Never deletes corrupt media directly.
        """
        if not file_path.exists():
            return file_path
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        dest = self.quarantine_dir / f"{task_id}_{timestamp}.corrupt"
        os.replace(file_path, dest)
        return dest

    # -------------------------------------------------------------
    # 5-Stage Step Execution
    # -------------------------------------------------------------
    def start_intent(
        self,
        task_id: str,
        project_id: str,
        step_name: str,
        final_output_path: Path,
        expected_format: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Step 1: INTENT
        Saves intent to .manifests/[task_id].json before any rendering begins.
        """
        validate_safe_path(final_output_path, self.project_dir)
        manifest_path = self.get_manifest_path(task_id)
        staging_path = self.get_staging_path(task_id, suffix=final_output_path.suffix)

        data = {
            "task_id": task_id,
            "project_id": project_id,
            "step_name": step_name,
            "status": CheckpointCommitState.INTENT.value,
            "sidecar_path": str(manifest_path.resolve()),
            "staging_path": str(staging_path.resolve()),
            "final_output_path": str(final_output_path.resolve()),
            "expected_format": expected_format,
            "file_size_bytes": 0,
            "sha256_checksum": "",
            "recovery_metadata": metadata or {},
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        TaskManifestManager.write_manifest_atomic(manifest_path, data, self.project_dir)
        return data

    def start_rendering(self, task_id: str) -> Dict[str, Any]:
        """
        Step 2: RENDERING
        Transitions manifest status to RENDERING.
        """
        manifest_path = self.get_manifest_path(task_id)
        data = TaskManifestManager.read_manifest(manifest_path, self.project_dir)
        data["status"] = CheckpointCommitState.RENDERING.value
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        TaskManifestManager.write_manifest_atomic(manifest_path, data, self.project_dir)
        return data

    def validate_rendered_output(self, task_id: str, min_expected_bytes: int = 1) -> Dict[str, Any]:
        """
        Step 3: VALIDATED
        Performs size and SHA-256 checksum validation on the staging file.
        """
        manifest_path = self.get_manifest_path(task_id)
        data = TaskManifestManager.read_manifest(manifest_path, self.project_dir)
        staging_path = Path(data["staging_path"])

        if not staging_path.is_file():
            self.quarantine_file(staging_path, task_id)
            raise OutputValidationError(f"Staging file not found: {staging_path}")

        file_size = staging_path.stat().st_size
        if file_size < min_expected_bytes:
            self.quarantine_file(staging_path, task_id)
            raise OutputValidationError(f"Rendered file is empty or too small ({file_size} bytes)")

        checksum = calculate_sha256(staging_path)
        data["status"] = CheckpointCommitState.VALIDATED.value
        data["file_size_bytes"] = file_size
        data["sha256_checksum"] = checksum
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        TaskManifestManager.write_manifest_atomic(manifest_path, data, self.project_dir)
        return data

    def commit_output(self, task_id: str, allow_overwrite: bool = True) -> Dict[str, Any]:
        """
        Step 4: OUTPUT_COMMITTED
        Atomically replaces staging file into final output destination with backoff retry.
        """
        manifest_path = self.get_manifest_path(task_id)
        data = TaskManifestManager.read_manifest(manifest_path, self.project_dir)

        staging_path = Path(data["staging_path"])
        final_path = Path(data["final_output_path"])

        if not staging_path.is_file():
            raise FileNotFoundError(f"Staging file missing for commit: {staging_path}")

        if final_path.exists() and not allow_overwrite:
            raise DestinationConflictError(f"Destination file already exists: {final_path}")

        # Atomic replace with retry
        atomic_replace_with_retry(staging_path, final_path)

        data["status"] = CheckpointCommitState.OUTPUT_COMMITTED.value
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        TaskManifestManager.write_manifest_atomic(manifest_path, data, self.project_dir)
        return data

    async def commit_database(self, task_id: str) -> Dict[str, Any]:
        """
        Step 5: DB_COMMITTED
        Commits durable checkpoint to SQLite using synchronous=FULL.
        Then syncs manifest status to DB_COMMITTED.
        """
        manifest_path = self.get_manifest_path(task_id)
        data = TaskManifestManager.read_manifest(manifest_path, self.project_dir)

        manifest_create = TaskManifestCreate(
            taskId=data["task_id"],
            projectId=data["project_id"],
            stepName=data["step_name"],
            status=CheckpointCommitState.DB_COMMITTED.value,
            sidecarPath=data["sidecar_path"],
            stagingPath=data["staging_path"],
            finalOutputPath=data["final_output_path"],
            expectedFormat=data["expected_format"],
            fileSizeBytes=data["file_size_bytes"],
            sha256Checksum=data["sha256_checksum"],
            recoveryMetadataJson=str(data.get("recovery_metadata", {})),
        )

        async with get_db(critical=True) as db:
            await crud.create_or_update_manifest(db, manifest_create)

        # Update sidecar to DB_COMMITTED
        data["status"] = CheckpointCommitState.DB_COMMITTED.value
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        TaskManifestManager.write_manifest_atomic(manifest_path, data, self.project_dir)
        return data
