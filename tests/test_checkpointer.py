"""
Unit tests for 5-Stage Checkpoint State Machine and Reconciliation Engine (Phase 5).
Tests: State transitions, Path Traversal (Case J), Quarantine (Case D), Corrupted Sidecar (Case G), Case K Idempotency.
"""
import pytest
from pathlib import Path
from app.config import CheckpointCommitState
from app.core.checkpointer import Checkpointer, calculate_sha256
from app.core.manifest import TaskManifestManager
from app.core.reconciliation import ReconciliationEngine
from app.db.database import get_db
from app.db import crud
from app.db.models import ProjectCreate, TaskManifestCreate


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_five_stage_checkpoint_lifecycle(tmp_path):
    """Verify standard 5-stage durable execution flow: INTENT -> RENDERING -> VALIDATED -> OUTPUT_COMMITTED -> DB_COMMITTED."""
    project_dir = tmp_path / "project_001"
    project_dir.mkdir()
    checkpointer = Checkpointer(project_dir)

    async with get_db(critical=True) as db:
        await crud.init_db(db)
        # Create parent project in DB first to satisfy foreign key
        proj = await crud.create_project(
            db,
            ProjectCreate(title="Test 001", mode="mode01_dubbing", inputVideoPath="test.mp4")
        )

        task_id = "task-dub-001"
        project_id = proj.id
        final_output = project_dir / "output.mp4"

        # Step 1: INTENT
        intent_data = checkpointer.start_intent(
            task_id=task_id,
            project_id=project_id,
            step_name="video_dubbing",
            final_output_path=final_output,
            expected_format="mp4",
        )
        assert intent_data["status"] == CheckpointCommitState.INTENT.value
        assert checkpointer.get_manifest_path(task_id).is_file()

        # Step 2: RENDERING
        render_data = checkpointer.start_rendering(task_id)
        assert render_data["status"] == CheckpointCommitState.RENDERING.value

        # Simulate render content in staging
        staging_file = Path(render_data["staging_path"])
        staging_file.write_bytes(b"Simulated MP4 media file binary stream 1234567890")

        # Step 3: VALIDATED
        val_data = checkpointer.validate_rendered_output(task_id, min_expected_bytes=10)
        assert val_data["status"] == CheckpointCommitState.VALIDATED.value
        assert val_data["sha256_checksum"] != ""
        assert val_data["file_size_bytes"] > 0

        # Step 4: OUTPUT_COMMITTED
        commit_data = checkpointer.commit_output(task_id)
        assert commit_data["status"] == CheckpointCommitState.OUTPUT_COMMITTED.value
        assert final_output.is_file()
        assert not staging_file.exists()

        # Step 5: DB_COMMITTED
        db_data = await checkpointer.commit_database(task_id)
        assert db_data["status"] == CheckpointCommitState.DB_COMMITTED.value

        # Verify in SQLite
        db_record = await crud.get_manifest(db, task_id)
        assert db_record is not None
        assert db_record.status == CheckpointCommitState.DB_COMMITTED.value

        # Clean up
        await crud.delete_project(db, proj.id)


@pytest.mark.anyio
async def test_case_j_path_traversal_protection(tmp_path):
    """Verify Case J: Path traversal escaping project directory is rejected."""
    project_dir = tmp_path / "project_002"
    project_dir.mkdir()
    checkpointer = Checkpointer(project_dir)

    malicious_path = tmp_path / "outside_project.mp4"

    with pytest.raises(ValueError, match="Path traversal detected"):
        checkpointer.start_intent(
            task_id="task-traversal",
            project_id="proj-002",
            step_name="step",
            final_output_path=malicious_path,
            expected_format="mp4",
        )


@pytest.mark.anyio
async def test_case_d_quarantine_corrupted_staging(tmp_path):
    """Verify Case D: Incomplete staging file during crash is quarantined and marked FAILED."""
    project_dir = tmp_path / "project_003"
    project_dir.mkdir()
    checkpointer = Checkpointer(project_dir)
    reconciler = ReconciliationEngine(project_dir)

    task_id = "task-crash-003"
    final_output = project_dir / "final.wav"

    # Start intent and rendering
    checkpointer.start_intent(task_id, "proj-003", "audio", final_output, "wav")
    render_data = checkpointer.start_rendering(task_id)

    # Incomplete 0-byte staging file left over from crash
    staging_file = Path(render_data["staging_path"])
    staging_file.touch()

    async with get_db(critical=True) as db:
        await crud.init_db(db)
        result = await reconciler.reconcile_single_task(task_id, db)
        assert result["case"] == "D"
        assert result["status"] == "quarantined_and_marked_failed"

        # Check quarantine folder has the corrupt file
        quarantined_files = list(checkpointer.quarantine_dir.glob("*.corrupt"))
        assert len(quarantined_files) == 1
        assert not staging_file.exists()


@pytest.mark.anyio
async def test_case_k_reconciliation_sidecar_sync(tmp_path):
    """Verify Case K: DB is DB_COMMITTED but sidecar was OUTPUT_COMMITTED -> sidecar is synced."""
    project_dir = tmp_path / "project_004"
    project_dir.mkdir()
    checkpointer = Checkpointer(project_dir)
    reconciler = ReconciliationEngine(project_dir)

    async with get_db(critical=True) as db:
        await crud.init_db(db)
        proj = await crud.create_project(
            db,
            ProjectCreate(title="Test Case K", mode="mode01_dubbing")
        )

        task_id = "task-case-k"
        final_output = project_dir / "vocals.wav"
        final_output.write_bytes(b"Valid audio content 123")
        checksum = calculate_sha256(final_output)

        # Setup sidecar at OUTPUT_COMMITTED
        manifest_path = checkpointer.get_manifest_path(task_id)
        sidecar_data = {
            "task_id": task_id,
            "project_id": proj.id,
            "step_name": "vocal_separation",
            "status": CheckpointCommitState.OUTPUT_COMMITTED.value,
            "sidecar_path": str(manifest_path.resolve()),
            "staging_path": str(project_dir / ".staging" / "vocals.tmp"),
            "final_output_path": str(final_output.resolve()),
            "expected_format": "wav",
            "file_size_bytes": final_output.stat().st_size,
            "sha256_checksum": checksum,
            "recovery_metadata": {},
            "updated_at": "2026-11-02T00:00:00",
        }
        TaskManifestManager.write_manifest_atomic(manifest_path, sidecar_data, project_dir)

        # Setup DB as DB_COMMITTED
        await crud.create_or_update_manifest(
            db,
            TaskManifestCreate(
                taskId=task_id,
                projectId=proj.id,
                stepName="vocal_separation",
                status="DB_COMMITTED",
                sidecarPath=str(manifest_path.resolve()),
                finalOutputPath=str(final_output.resolve()),
                sha256Checksum=checksum,
            )
        )

        res = await reconciler.reconcile_single_task(task_id, db)
        assert res["case"] == "K"
        assert res["status"] == "sidecar_synced_to_db_committed"

        # Verify sidecar was updated to DB_COMMITTED
        updated_sidecar = TaskManifestManager.read_manifest(manifest_path, project_dir)
        assert updated_sidecar["status"] == CheckpointCommitState.DB_COMMITTED.value

        # Clean up
        await crud.delete_project(db, proj.id)
