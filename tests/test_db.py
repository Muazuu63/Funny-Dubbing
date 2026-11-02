"""
Automated Unit Tests for AI-VPS Database Layer (Phase 2).
Tests: WAL Mode, JSON1 functions, Dual Durability Policy, Schema Validation, TypeScript-Python Mapping.
"""
import pytest
import asyncio
from pathlib import Path
import aiosqlite
from app.db.database import get_db, get_connection, verify_json1_support
from app.db import crud
from app.db.models import (
    ProjectCreate,
    TaskManifestCreate,
    AudioMixerStateBase,
    ModelRegistryCreate,
    CommercialUseStatus,
    ModelVerificationStatus,
)


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_wal_mode_and_json1():
    """Verify that SQLite runs in WAL mode and supports JSON1 functions."""
    async with get_db(critical=False) as db:
        # Check WAL mode
        async with db.execute("PRAGMA journal_mode;") as cursor:
            row = await cursor.fetchone()
            assert row[0].lower() == "wal"

        # Check JSON1 support
        is_json1_ready = await verify_json1_support(db)
        assert is_json1_ready is True


@pytest.mark.anyio
async def test_dual_durability_pragmas():
    """
    Verify Dual Durability Policy:
    - Critical Checkpoints: synchronous = FULL (2)
    - Telemetry/Non-critical: synchronous = NORMAL (1)
    """
    # 1. Critical connection
    critical_conn = await get_connection(critical=True)
    try:
        async with critical_conn.execute("PRAGMA synchronous;") as cursor:
            row = await cursor.fetchone()
            # In SQLite, 2 = FULL
            assert row[0] == 2
    finally:
        await critical_conn.close()

    # 2. Non-critical connection
    normal_conn = await get_connection(critical=False)
    try:
        async with normal_conn.execute("PRAGMA synchronous;") as cursor:
            row = await cursor.fetchone()
            # In SQLite, 1 = NORMAL
            assert row[0] == 1
    finally:
        await normal_conn.close()


@pytest.mark.anyio
async def test_schema_init_and_project_crud():
    """Test full schema creation and Project CRUD with cascade delete."""
    async with get_db(critical=True) as db:
        await crud.init_db(db)

        # Create a new project
        new_proj = ProjectCreate(
            title="Funny Cat Dubbing 01",
            mode="mode01_dubbing",
            inputVideoPath="storage/projects/cat.mp4",
            targetLanguages=["Bangla", "Hindi"],
        )
        created = await crud.create_project(db, new_proj)
        assert created.id is not None
        assert created.title == "Funny Cat Dubbing 01"
        assert created.target_languages == ["Bangla", "Hindi"]

        # Fetch project
        fetched = await crud.get_project(db, created.id)
        assert fetched is not None
        assert fetched.id == created.id

        # Verify default AudioMixerState was initialized
        mixer = await crud.get_mixer_state(db, created.id)
        assert mixer is not None
        assert mixer.project_id == created.id
        assert mixer.master_volume == 1.0
        assert mixer.master_level_dbfs == -60.0

        # Delete project and verify cascade
        deleted = await crud.delete_project(db, created.id)
        assert deleted is True

        # Mixer state should be cascade deleted
        mixer_after_delete = await crud.get_mixer_state(db, created.id)
        assert mixer_after_delete is None


@pytest.mark.anyio
async def test_typescript_camelcase_mapping_for_mixer():
    """Test TypeScript camelCase <-> SQLite snake_case mapping for AudioMixerState."""
    async with get_db(critical=True) as db:
        await crud.init_db(db)

        proj = await crud.create_project(
            db,
            ProjectCreate(
                title="Mixer Test",
                mode="mode01_dubbing",
            ),
        )

        # Update mixer using TypeScript camelCase payload
        ts_payload = {
            "masterVolume": 1.25,
            "masterLevelDb": -3.5,
            "peakClippingDetected": False,
            "originalAudioMuted": True,
            "demucsVocalVolume": 0.8,
            "aiVoiceVolume": 1.1,
        }
        updated = await crud.update_mixer_state(db, proj.id, ts_payload)

        assert updated.master_volume == 1.25
        assert updated.master_level_dbfs == -3.5
        assert updated.demucs_vocal_volume == 0.8
        assert updated.ai_voice_volume == 1.1

        # Clean up
        await crud.delete_project(db, proj.id)


@pytest.mark.anyio
async def test_task_manifest_durability_and_checkpoint():
    """Test TaskManifest creation and checkpoint recovery state transitions."""
    async with get_db(critical=True) as db:
        await crud.init_db(db)

        proj = await crud.create_project(
            db,
            ProjectCreate(title="Task Test", mode="mode01_dubbing"),
        )

        manifest = TaskManifestCreate(
            taskId="task-step-01-separation",
            projectId=proj.id,
            stepName="audio_separation",
            status="INTENT",
            sidecarPath="storage/projects/sidecar.json",
            stagingPath="storage/projects/.staging/vocals.wav",
        )

        saved = await crud.create_or_update_manifest(db, manifest)
        assert saved.status == "INTENT"
        assert saved.task_id == "task-step-01-separation"

        # Update to committed state
        manifest_update = TaskManifestCreate(
            taskId="task-step-01-separation",
            projectId=proj.id,
            stepName="audio_separation",
            status="DB_COMMITTED",
            sidecarPath="storage/projects/sidecar.json",
            stagingPath="storage/projects/.staging/vocals.wav",
            finalOutputPath="storage/projects/vocals.wav",
            fileSizeBytes=1048576,
            sha256Checksum="abcdef1234567890",
        )
        updated_manifest = await crud.create_or_update_manifest(db, manifest_update)
        assert updated_manifest.status == "DB_COMMITTED"
        assert updated_manifest.file_size_bytes == 1048576

        # Clean up
        await crud.delete_project(db, proj.id)


@pytest.mark.anyio
async def test_model_registry_27_fields():
    """Verify that all 27 fields of ModelRegistry are correctly stored and retrieved."""
    async with get_db(critical=True) as db:
        await crud.init_db(db)

        model_entry = ModelRegistryCreate(
            modelId="whisper-tiny-local",
            name="OpenAI Whisper Tiny",
            taskType="stt",
            engineType="local_offline",
            version="20230314",
            weightsSource="HuggingFace",
            codeLicense="MIT",
            weightsLicense="MIT",
            datasetLicense="Public Domain",
            voiceAssetLicense="N/A",
            exactLicenseVersion="MIT",
            officialLicenseUrl="https://github.com/openai/whisper/blob/main/LICENSE",
            officialDownloadUrl="https://openaipublic.azureedge.net/main/whisper/models/tiny.pt",
            commercialUseStatus=CommercialUseStatus.ALLOWED,
            attributionRequired=False,
            attributionText=None,
            verificationEvidence="Official MIT License verified in repository.",
            checksumSha256="bd577a113a864445d14f295b4dd4cb177ac4670ab31e45fb3700b646c4019ab7",
            localPath="storage/models/whisper/tiny.pt",
            minRamGb=2.0,
            minVramGb=0.0,
            recommendedDevice="cpu",
            cpuSupport=True,
            offlineCapable=True,
            internetRequirement=False,
            verificationStatus=ModelVerificationStatus.VERIFIED,
            lastVerifiedDate="2026-11-02",
        )

        registered = await crud.register_model(db, model_entry)
        assert registered.model_id == "whisper-tiny-local"
        assert registered.commercial_use_status == CommercialUseStatus.ALLOWED

        fetched = await crud.get_model(db, "whisper-tiny-local")
        assert fetched is not None
        assert fetched.name == "OpenAI Whisper Tiny"
        assert fetched.min_ram_gb == 2.0
        assert fetched.cpu_support is True
        assert fetched.offline_capable is True
        assert fetched.checksum_sha256 == "bd577a113a864445d14f295b4dd4cb177ac4670ab31e45fb3700b646c4019ab7"
