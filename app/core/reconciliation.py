"""
Startup and Crash Reconciliation Engine for AI-VPS.
Master Architecture v2.2 & PRD v2.2 Aligned.

Implements Authoritative Conflict Rule:
Verified disk media files & sidecar manifests are Physical Ground Truth; SQLite is relational index.
Executes Cases A through K idempotently.
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import aiosqlite

from app.config import CheckpointCommitState, settings
from app.core.checkpointer import Checkpointer, calculate_sha256, atomic_replace_with_retry
from app.core.manifest import TaskManifestManager, ManifestCorruptedError
from app.core.security import validate_safe_path
from app.db import crud
from app.db.models import TaskManifestCreate

logger = logging.getLogger("ai_vps.reconciliation")


class ReconciliationEngine:
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.checkpointer = Checkpointer(project_dir)

    async def reconcile_single_task(self, task_id: str, db: aiosqlite.Connection) -> Dict[str, Any]:
        """
        Reconciles a single task checkpoint against disk ground truth and SQLite.
        Strictly idempotent.
        """
        manifest_path = self.checkpointer.get_manifest_path(task_id)

        # -------------------------------------------------------------
        # Case J: Path Traversal Check
        # -------------------------------------------------------------
        try:
            validate_safe_path(manifest_path, self.project_dir)
        except ValueError as ve:
            raise SecurityError(f"Case J: Path Traversal detected during reconciliation: {ve}") from ve

        # -------------------------------------------------------------
        # Case G: Sidecar Corrupted / Unreadable Check
        # -------------------------------------------------------------
        sidecar_data: Optional[Dict[str, Any]] = None
        try:
            if manifest_path.is_file():
                sidecar_data = TaskManifestManager.read_manifest(manifest_path, self.project_dir)
        except ManifestCorruptedError:
            # Query SQLite for fallback reconstruction
            db_record = await crud.get_manifest(db, task_id)
            if db_record and db_record.final_output_path:
                final_p = Path(db_record.final_output_path)
                if final_p.is_file() and calculate_sha256(final_p) == db_record.sha256_checksum:
                    # Reconstruct sidecar from DB
                    sidecar_data = {
                        "task_id": db_record.task_id,
                        "project_id": db_record.project_id,
                        "step_name": db_record.step_name,
                        "status": db_record.status,
                        "sidecar_path": str(manifest_path.resolve()),
                        "staging_path": db_record.staging_path,
                        "final_output_path": db_record.final_output_path,
                        "expected_format": db_record.expected_format,
                        "file_size_bytes": db_record.file_size_bytes,
                        "sha256_checksum": db_record.sha256_checksum,
                        "recovery_metadata": {},
                        "updated_at": db_record.updated_at,
                    }
                    TaskManifestManager.write_manifest_atomic(manifest_path, sidecar_data, self.project_dir)
                    return {"task_id": task_id, "case": "G", "status": "sidecar_rebuilt_from_db"}
            
            # If not in DB, quarantine corrupt sidecar
            self.checkpointer.quarantine_file(manifest_path, task_id)
            return {"task_id": task_id, "case": "G", "status": "quarantined_corrupt_sidecar"}

        if not sidecar_data:
            return {"task_id": task_id, "case": "MISSING", "status": "no_manifest_found"}

        sidecar_status = sidecar_data.get("status")
        final_path = Path(sidecar_data["final_output_path"]) if sidecar_data.get("final_output_path") else None
        staging_path = Path(sidecar_data["staging_path"]) if sidecar_data.get("staging_path") else None
        expected_checksum = sidecar_data.get("sha256_checksum", "")

        final_valid = (
            final_path is not None
            and final_path.is_file()
            and (not expected_checksum or calculate_sha256(final_path) == expected_checksum)
        )
        staging_valid = (
            staging_path is not None
            and staging_path.is_file()
            and staging_path.stat().st_size > 0
        )

        db_manifest = await crud.get_manifest(db, task_id)
        db_status = db_manifest.status if db_manifest else None

        # -------------------------------------------------------------
        # Case H: DB Record Missing, Sidecar & Final File Valid
        # -------------------------------------------------------------
        if not db_manifest and final_valid and sidecar_status in (CheckpointCommitState.OUTPUT_COMMITTED.value, CheckpointCommitState.DB_COMMITTED.value):
            manifest_create = TaskManifestCreate(
                taskId=sidecar_data["task_id"],
                projectId=sidecar_data["project_id"],
                stepName=sidecar_data["step_name"],
                status=CheckpointCommitState.DB_COMMITTED.value,
                sidecarPath=sidecar_data["sidecar_path"],
                stagingPath=sidecar_data["staging_path"],
                finalOutputPath=sidecar_data["final_output_path"],
                expectedFormat=sidecar_data["expected_format"],
                fileSizeBytes=sidecar_data["file_size_bytes"],
                sha256Checksum=sidecar_data["sha256_checksum"],
                recoveryMetadataJson=str(sidecar_data.get("recovery_metadata", {})),
            )
            await crud.create_or_update_manifest(db, manifest_create)
            sidecar_data["status"] = CheckpointCommitState.DB_COMMITTED.value
            TaskManifestManager.write_manifest_atomic(manifest_path, sidecar_data, self.project_dir)
            return {"task_id": task_id, "case": "H", "status": "db_record_reconstructed"}

        # -------------------------------------------------------------
        # Case A: Both DB & Sidecar DB_COMMITTED, Final File Valid
        # -------------------------------------------------------------
        if sidecar_status == CheckpointCommitState.DB_COMMITTED.value and db_status in ("DB_COMMITTED", "COMPLETED") and final_valid:
            return {"task_id": task_id, "case": "A", "status": "verified_noop"}

        # -------------------------------------------------------------
        # Case K: DB is COMPLETED/DB_COMMITTED, Sidecar is OUTPUT_COMMITTED
        # (SQLite commit succeeded, but process crashed before sidecar updated)
        # -------------------------------------------------------------
        if db_status in ("DB_COMMITTED", "COMPLETED") and sidecar_status == CheckpointCommitState.OUTPUT_COMMITTED.value and final_valid:
            sidecar_data["status"] = CheckpointCommitState.DB_COMMITTED.value
            TaskManifestManager.write_manifest_atomic(manifest_path, sidecar_data, self.project_dir)
            return {"task_id": task_id, "case": "K", "status": "sidecar_synced_to_db_committed"}

        # -------------------------------------------------------------
        # Case B: Sidecar is OUTPUT_COMMITTED, DB is in-progress, Final File Valid
        # -------------------------------------------------------------
        if sidecar_status == CheckpointCommitState.OUTPUT_COMMITTED.value and final_valid:
            # Fast-forward DB and sidecar
            manifest_create = TaskManifestCreate(
                taskId=sidecar_data["task_id"],
                projectId=sidecar_data["project_id"],
                stepName=sidecar_data["step_name"],
                status=CheckpointCommitState.DB_COMMITTED.value,
                sidecarPath=sidecar_data["sidecar_path"],
                stagingPath=sidecar_data["staging_path"],
                finalOutputPath=sidecar_data["final_output_path"],
                expectedFormat=sidecar_data["expected_format"],
                fileSizeBytes=sidecar_data["file_size_bytes"],
                sha256Checksum=sidecar_data["sha256_checksum"],
                recoveryMetadataJson=str(sidecar_data.get("recovery_metadata", {})),
            )
            await crud.create_or_update_manifest(db, manifest_create)
            sidecar_data["status"] = CheckpointCommitState.DB_COMMITTED.value
            TaskManifestManager.write_manifest_atomic(manifest_path, sidecar_data, self.project_dir)
            return {"task_id": task_id, "case": "B", "status": "fast_forwarded_to_completed"}

        # -------------------------------------------------------------
        # Case C: Staging Valid, Status is VALIDATED or RENDERING
        # -------------------------------------------------------------
        if staging_valid and sidecar_status in (CheckpointCommitState.VALIDATED.value, CheckpointCommitState.RENDERING.value):
            # Atomic replace to final output
            atomic_replace_with_retry(staging_path, final_path)
            checksum = calculate_sha256(final_path)
            sidecar_data["sha256_checksum"] = checksum
            sidecar_data["file_size_bytes"] = final_path.stat().st_size
            sidecar_data["status"] = CheckpointCommitState.DB_COMMITTED.value
            TaskManifestManager.write_manifest_atomic(manifest_path, sidecar_data, self.project_dir)

            manifest_create = TaskManifestCreate(
                taskId=sidecar_data["task_id"],
                projectId=sidecar_data["project_id"],
                stepName=sidecar_data["step_name"],
                status=CheckpointCommitState.DB_COMMITTED.value,
                sidecarPath=sidecar_data["sidecar_path"],
                stagingPath=sidecar_data["staging_path"],
                finalOutputPath=sidecar_data["final_output_path"],
                expectedFormat=sidecar_data["expected_format"],
                fileSizeBytes=sidecar_data["file_size_bytes"],
                sha256Checksum=checksum,
                recoveryMetadataJson=str(sidecar_data.get("recovery_metadata", {})),
            )
            await crud.create_or_update_manifest(db, manifest_create)
            return {"task_id": task_id, "case": "C", "status": "replaced_and_committed"}

        # -------------------------------------------------------------
        # Case D: RENDERING / INTENT with Corrupted / Incomplete Staging File
        # -------------------------------------------------------------
        if sidecar_status in (CheckpointCommitState.RENDERING.value, CheckpointCommitState.INTENT.value) and not final_valid:
            if staging_path and staging_path.exists():
                self.checkpointer.quarantine_file(staging_path, task_id)
            sidecar_data["status"] = "FAILED"
            sidecar_data["recovery_metadata"]["failure_reason"] = "Incomplete/Corrupted staging during crash."
            TaskManifestManager.write_manifest_atomic(manifest_path, sidecar_data, self.project_dir)

            if db_manifest:
                db_manifest_create = TaskManifestCreate(
                    taskId=task_id,
                    projectId=sidecar_data["project_id"],
                    stepName=sidecar_data["step_name"],
                    status="FAILED",
                    sidecarPath=sidecar_data["sidecar_path"],
                    stagingPath=sidecar_data["staging_path"],
                    finalOutputPath=sidecar_data["final_output_path"],
                    expectedFormat=sidecar_data["expected_format"],
                    fileSizeBytes=0,
                    sha256Checksum="",
                    recoveryMetadataJson=json.dumps(sidecar_data["recovery_metadata"]),
                )
                await crud.create_or_update_manifest(db, db_manifest_create)
            return {"task_id": task_id, "case": "D", "status": "quarantined_and_marked_failed"}

        # -------------------------------------------------------------
        # Case E: Final File Valid, Staging Missing, DB In-Progress
        # -------------------------------------------------------------
        if final_valid and (not staging_path or not staging_path.exists()) and db_status != "DB_COMMITTED":
            manifest_create = TaskManifestCreate(
                taskId=sidecar_data["task_id"],
                projectId=sidecar_data["project_id"],
                stepName=sidecar_data["step_name"],
                status=CheckpointCommitState.DB_COMMITTED.value,
                sidecarPath=sidecar_data["sidecar_path"],
                stagingPath=sidecar_data["staging_path"],
                finalOutputPath=sidecar_data["final_output_path"],
                expectedFormat=sidecar_data["expected_format"],
                fileSizeBytes=final_path.stat().st_size,
                sha256Checksum=calculate_sha256(final_path),
                recoveryMetadataJson=str(sidecar_data.get("recovery_metadata", {})),
            )
            await crud.create_or_update_manifest(db, manifest_create)
            sidecar_data["status"] = CheckpointCommitState.DB_COMMITTED.value
            TaskManifestManager.write_manifest_atomic(manifest_path, sidecar_data, self.project_dir)
            return {"task_id": task_id, "case": "E", "status": "fast_forwarded_final_valid"}

        # Default fallback
        return {"task_id": task_id, "case": "UNHANDLED", "status": sidecar_status}


async def reconcile_tasks_on_startup() -> Dict[str, Any]:
    """Scans all projects in storage/projects and reconciles interrupted tasks."""
    projects_dir = settings.PROJECTS_DIR
    recovered_count = 0
    failed_count = 0

    if not projects_dir.exists():
        return {"recovered": 0, "failed": 0}

    from app.db.database import get_db
    async with get_db(critical=True) as db:
        for proj_folder in projects_dir.iterdir():
            if proj_folder.is_dir() and (proj_folder / ".manifests").exists():
                engine = ReconciliationEngine(proj_folder)
                for manifest_file in (proj_folder / ".manifests").glob("*.json"):
                    task_id = manifest_file.stem
                    res = await engine.reconcile_single_task(task_id, db)
                    if "committed" in res.get("status", "") or "verified" in res.get("status", ""):
                        recovered_count += 1
                    elif "failed" in res.get("status", ""):
                        failed_count += 1

    return {"recovered": recovered_count, "failed": failed_count}
