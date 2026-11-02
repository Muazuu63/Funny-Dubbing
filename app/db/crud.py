"""
CRUD and Database Initialization Operations for AI-VPS.
Master Architecture v2.2 & PRD v2.2 Aligned.
Uses parameterized queries to prevent SQL Injection and guarantees Dual Durability transactions.
"""
import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import aiosqlite

from app.db.models import (
    Project,
    ProjectCreate,
    TaskManifest,
    TaskManifestCreate,
    Script,
    ScriptCreate,
    ScriptApprovalStatus,
    AudioMixerState,
    AudioMixerStateCreate,
    SystemSettings,
    ModelRegistry,
    ModelRegistryCreate,
    CommercialUseStatus,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def init_db(db: aiosqlite.Connection) -> None:
    """
    Initializes the SQLite database with all 6 required schemas.
    Enforces Foreign Keys, WAL mode and JSON1 compatibility.
    """
    await db.execute("PRAGMA foreign_keys = ON;")
    
    # 1. Projects Table
    await db.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            mode TEXT NOT NULL,
            input_video_path TEXT,
            target_languages TEXT NOT NULL DEFAULT '["Bangla"]',
            status TEXT NOT NULL DEFAULT 'CREATED',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
    """)

    # 2. Task Manifests Table (Critical Checkpoints)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS task_manifests (
            task_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            step_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'INTENT',
            sidecar_path TEXT,
            staging_path TEXT,
            final_output_path TEXT,
            expected_format TEXT,
            file_size_bytes INTEGER DEFAULT 0,
            sha256_checksum TEXT,
            recovery_metadata_json TEXT DEFAULT '{}',
            updated_at TEXT NOT NULL
        );
    """)

    # 3. Scripts Table
    await db.execute("""
        CREATE TABLE IF NOT EXISTS scripts (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            script_title TEXT NOT NULL,
            scenes_json TEXT NOT NULL,
            selected_flag INTEGER NOT NULL DEFAULT 0,
            approval_status TEXT NOT NULL DEFAULT 'PENDING',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
    """)

    # 4. Audio Mixer States Table (Telemetry & Non-critical)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS audio_mixer_states (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL UNIQUE REFERENCES projects(id) ON DELETE CASCADE,
            original_audio_volume REAL NOT NULL DEFAULT 1.0,
            original_audio_muted INTEGER NOT NULL DEFAULT 1,
            demucs_vocal_volume REAL NOT NULL DEFAULT 1.0,
            demucs_accompaniment_volume REAL NOT NULL DEFAULT 1.0,
            ai_voice_volume REAL NOT NULL DEFAULT 1.0,
            master_volume REAL NOT NULL DEFAULT 1.0,
            master_level_dbfs REAL NOT NULL DEFAULT -60.0,
            peak_clipping_detected INTEGER NOT NULL DEFAULT 0,
            hard_limiter_enabled INTEGER NOT NULL DEFAULT 1,
            normalizer_enabled INTEGER NOT NULL DEFAULT 1,
            normalizer_target_lufs REAL NOT NULL DEFAULT -16.0,
            updated_at TEXT NOT NULL
        );
    """)

    # 5. System Settings Table
    await db.execute("""
        CREATE TABLE IF NOT EXISTS system_settings (
            id TEXT PRIMARY KEY,
            verified_free_models TEXT NOT NULL DEFAULT '[]',
            active_gemini_model TEXT NOT NULL DEFAULT 'gemini-1.5-flash',
            offline_mode_enabled INTEGER NOT NULL DEFAULT 0,
            commercial_mode_strict INTEGER NOT NULL DEFAULT 1,
            updated_at TEXT NOT NULL
        );
    """)

    # 6. Model Commercial License Registry Table (All 27 Fields)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS model_registry (
            model_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            task_type TEXT NOT NULL,
            engine_type TEXT NOT NULL,
            version TEXT NOT NULL DEFAULT '1.0.0',
            weights_source TEXT NOT NULL,
            code_license TEXT NOT NULL,
            weights_license TEXT NOT NULL,
            dataset_license TEXT NOT NULL,
            voice_asset_license TEXT NOT NULL,
            exact_license_version TEXT NOT NULL,
            official_license_url TEXT NOT NULL,
            official_download_url TEXT NOT NULL,
            commercial_use_status TEXT NOT NULL DEFAULT 'ALLOWED',
            attribution_required INTEGER NOT NULL DEFAULT 0,
            attribution_text TEXT,
            verification_evidence TEXT NOT NULL,
            checksum_sha256 TEXT NOT NULL,
            local_path TEXT NOT NULL,
            min_ram_gb REAL NOT NULL DEFAULT 4.0,
            min_vram_gb REAL NOT NULL DEFAULT 0.0,
            recommended_device TEXT NOT NULL DEFAULT 'cpu',
            cpu_support INTEGER NOT NULL DEFAULT 1,
            offline_capable INTEGER NOT NULL DEFAULT 1,
            internet_requirement INTEGER NOT NULL DEFAULT 0,
            verification_status TEXT NOT NULL DEFAULT 'UNVERIFIED',
            last_verified_date TEXT NOT NULL
        );
    """)

    # Create Indexes for query optimization
    await db.execute("CREATE INDEX IF NOT EXISTS idx_tasks_project ON task_manifests(project_id);")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON task_manifests(status);")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_scripts_project ON scripts(project_id);")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_models_task ON model_registry(task_type);")

    # Insert default system settings if not exists
    cursor = await db.execute("SELECT id FROM system_settings WHERE id = 'default';")
    if not await cursor.fetchone():
        await db.execute(
            """
            INSERT INTO system_settings (id, verified_free_models, active_gemini_model, offline_mode_enabled, commercial_mode_strict, updated_at)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            ("default", "[]", "gemini-1.5-flash", 0, 1, _utc_now_iso())
        )

    await db.commit()


# ==========================================
# Project CRUD
# ==========================================
async def create_project(db: aiosqlite.Connection, project: ProjectCreate) -> Project:
    project_id = str(uuid.uuid4())
    now = _utc_now_iso()
    target_languages_json = json.dumps(project.target_languages)
    
    await db.execute(
        """
        INSERT INTO projects (id, title, mode, input_video_path, target_languages, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            project_id,
            project.title,
            project.mode,
            project.input_video_path,
            target_languages_json,
            project.status,
            now,
            now,
        )
    )
    
    # Also initialize default AudioMixerState for this project
    mixer_id = str(uuid.uuid4())
    await db.execute(
        """
        INSERT INTO audio_mixer_states (
            id, project_id, original_audio_volume, original_audio_muted,
            demucs_vocal_volume, demucs_accompaniment_volume, ai_voice_volume,
            master_volume, master_level_dbfs, peak_clipping_detected,
            hard_limiter_enabled, normalizer_enabled, normalizer_target_lufs, updated_at
        ) VALUES (?, ?, 1.0, 1, 1.0, 1.0, 1.0, 1.0, -60.0, 0, 1, 1, -16.0, ?);
        """,
        (mixer_id, project_id, now)
    )
    
    await db.commit()
    
    return Project(
        id=project_id,
        title=project.title,
        mode=project.mode,
        input_video_path=project.input_video_path,
        target_languages=project.target_languages,
        status=project.status,
        created_at=now,
        updated_at=now,
    )


async def get_project(db: aiosqlite.Connection, project_id: str) -> Optional[Project]:
    async with db.execute("SELECT * FROM projects WHERE id = ?;", (project_id,)) as cursor:
        row = await cursor.fetchone()
        if not row:
            return None
        return Project(
            id=row["id"],
            title=row["title"],
            mode=row["mode"],
            input_video_path=row["input_video_path"],
            target_languages=json.loads(row["target_languages"]),
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


async def list_projects(db: aiosqlite.Connection) -> List[Project]:
    async with db.execute("SELECT * FROM projects ORDER BY created_at DESC;") as cursor:
        rows = await cursor.fetchall()
        return [
            Project(
                id=row["id"],
                title=row["title"],
                mode=row["mode"],
                input_video_path=row["input_video_path"],
                target_languages=json.loads(row["target_languages"]),
                status=row["status"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]


async def delete_project(db: aiosqlite.Connection, project_id: str) -> bool:
    cursor = await db.execute("DELETE FROM projects WHERE id = ?;", (project_id,))
    await db.commit()
    return cursor.rowcount > 0


# ==========================================
# Task Manifest CRUD (Critical Durability)
# ==========================================
async def create_or_update_manifest(db: aiosqlite.Connection, manifest: TaskManifestCreate) -> TaskManifest:
    """
    Creates or updates a durable task checkpoint.
    """
    now = _utc_now_iso()
    await db.execute(
        """
        INSERT INTO task_manifests (
            task_id, project_id, step_name, status, sidecar_path,
            staging_path, final_output_path, expected_format,
            file_size_bytes, sha256_checksum, recovery_metadata_json, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(task_id) DO UPDATE SET
            status=excluded.status,
            sidecar_path=excluded.sidecar_path,
            staging_path=excluded.staging_path,
            final_output_path=excluded.final_output_path,
            expected_format=excluded.expected_format,
            file_size_bytes=excluded.file_size_bytes,
            sha256_checksum=excluded.sha256_checksum,
            recovery_metadata_json=excluded.recovery_metadata_json,
            updated_at=excluded.updated_at;
        """,
        (
            manifest.task_id,
            manifest.project_id,
            manifest.step_name,
            manifest.status,
            manifest.sidecar_path,
            manifest.staging_path,
            manifest.final_output_path,
            manifest.expected_format,
            manifest.file_size_bytes,
            manifest.sha256_checksum,
            manifest.recovery_metadata_json,
            now,
        )
    )
    await db.commit()
    
    return TaskManifest(
        task_id=manifest.task_id,
        project_id=manifest.project_id,
        step_name=manifest.step_name,
        status=manifest.status,
        sidecar_path=manifest.sidecar_path,
        staging_path=manifest.staging_path,
        final_output_path=manifest.final_output_path,
        expected_format=manifest.expected_format,
        file_size_bytes=manifest.file_size_bytes,
        sha256_checksum=manifest.sha256_checksum,
        recovery_metadata_json=manifest.recovery_metadata_json,
        updated_at=now,
    )


async def get_manifest(db: aiosqlite.Connection, task_id: str) -> Optional[TaskManifest]:
    async with db.execute("SELECT * FROM task_manifests WHERE task_id = ?;", (task_id,)) as cursor:
        row = await cursor.fetchone()
        if not row:
            return None
        return TaskManifest(
            task_id=row["task_id"],
            project_id=row["project_id"],
            step_name=row["step_name"],
            status=row["status"],
            sidecar_path=row["sidecar_path"],
            staging_path=row["staging_path"],
            final_output_path=row["final_output_path"],
            expected_format=row["expected_format"],
            file_size_bytes=row["file_size_bytes"],
            sha256_checksum=row["sha256_checksum"],
            recovery_metadata_json=row["recovery_metadata_json"],
            updated_at=row["updated_at"],
        )


async def list_manifests_by_project(db: aiosqlite.Connection, project_id: str) -> List[TaskManifest]:
    async with db.execute("SELECT * FROM task_manifests WHERE project_id = ? ORDER BY updated_at ASC;", (project_id,)) as cursor:
        rows = await cursor.fetchall()
        return [
            TaskManifest(
                task_id=row["task_id"],
                project_id=row["project_id"],
                step_name=row["step_name"],
                status=row["status"],
                sidecar_path=row["sidecar_path"],
                staging_path=row["staging_path"],
                final_output_path=row["final_output_path"],
                expected_format=row["expected_format"],
                file_size_bytes=row["file_size_bytes"],
                sha256_checksum=row["sha256_checksum"],
                recovery_metadata_json=row["recovery_metadata_json"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]


# ==========================================
# Audio Mixer State CRUD (Telemetry / Non-Critical)
# ==========================================
async def get_mixer_state(db: aiosqlite.Connection, project_id: str) -> Optional[AudioMixerState]:
    async with db.execute("SELECT * FROM audio_mixer_states WHERE project_id = ?;", (project_id,)) as cursor:
        row = await cursor.fetchone()
        if not row:
            return None
        return AudioMixerState(
            id=row["id"],
            project_id=row["project_id"],
            original_audio_volume=row["original_audio_volume"],
            original_audio_muted=bool(row["original_audio_muted"]),
            demucs_vocal_volume=row["demucs_vocal_volume"],
            demucs_accompaniment_volume=row["demucs_accompaniment_volume"],
            ai_voice_volume=row["ai_voice_volume"],
            master_volume=row["master_volume"],
            master_level_dbfs=row["master_level_dbfs"],
            peak_clipping_detected=bool(row["peak_clipping_detected"]),
            hard_limiter_enabled=bool(row["hard_limiter_enabled"]),
            normalizer_enabled=bool(row["normalizer_enabled"]),
            normalizer_target_lufs=row["normalizer_target_lufs"],
            updated_at=row["updated_at"],
        )


async def update_mixer_state(db: aiosqlite.Connection, project_id: str, updates: Dict[str, Any]) -> AudioMixerState:
    now = _utc_now_iso()
    # Map possible TypeScript alias names to SQLite column names
    field_map = {
        "originalAudioVolume": "original_audio_volume",
        "originalAudioMuted": "original_audio_muted",
        "demucsVocalVolume": "demucs_vocal_volume",
        "demucsAccompanimentVolume": "demucs_accompaniment_volume",
        "aiVoiceVolume": "ai_voice_volume",
        "masterVolume": "master_volume",
        "masterLevelDb": "master_level_dbfs",
        "masterLevelDbfs": "master_level_dbfs",
        "peakClippingDetected": "peak_clipping_detected",
        "hardLimiterEnabled": "hard_limiter_enabled",
        "normalizerEnabled": "normalizer_enabled",
        "normalizerTargetLufs": "normalizer_target_lufs",
    }
    
    cleaned_updates: Dict[str, Any] = {}
    for k, v in updates.items():
        db_col = field_map.get(k, k)
        cleaned_updates[db_col] = v
        
    cleaned_updates["updated_at"] = now
    
    clauses = [f"{col} = ?" for col in cleaned_updates.keys()]
    values = list(cleaned_updates.values()) + [project_id]
    
    await db.execute(
        f"UPDATE audio_mixer_states SET {', '.join(clauses)} WHERE project_id = ?;",
        values
    )
    await db.commit()
    
    state = await get_mixer_state(db, project_id)
    if not state:
        raise ValueError(f"Mixer state not found for project: {project_id}")
    return state


# ==========================================
# Model Registry CRUD (All 27 Fields)
# ==========================================
async def register_model(db: aiosqlite.Connection, model: ModelRegistryCreate) -> ModelRegistry:
    await db.execute(
        """
        INSERT INTO model_registry (
            model_id, name, task_type, engine_type, version, weights_source,
            code_license, weights_license, dataset_license, voice_asset_license,
            exact_license_version, official_license_url, official_download_url,
            commercial_use_status, attribution_required, attribution_text,
            verification_evidence, checksum_sha256, local_path, min_ram_gb,
            min_vram_gb, recommended_device, cpu_support, offline_capable,
            internet_requirement, verification_status, last_verified_date
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        ON CONFLICT(model_id) DO UPDATE SET
            name=excluded.name,
            task_type=excluded.task_type,
            engine_type=excluded.engine_type,
            version=excluded.version,
            weights_source=excluded.weights_source,
            code_license=excluded.code_license,
            weights_license=excluded.weights_license,
            dataset_license=excluded.dataset_license,
            voice_asset_license=excluded.voice_asset_license,
            exact_license_version=excluded.exact_license_version,
            official_license_url=excluded.official_license_url,
            official_download_url=excluded.official_download_url,
            commercial_use_status=excluded.commercial_use_status,
            attribution_required=excluded.attribution_required,
            attribution_text=excluded.attribution_text,
            verification_evidence=excluded.verification_evidence,
            checksum_sha256=excluded.checksum_sha256,
            local_path=excluded.local_path,
            min_ram_gb=excluded.min_ram_gb,
            min_vram_gb=excluded.min_vram_gb,
            recommended_device=excluded.recommended_device,
            cpu_support=excluded.cpu_support,
            offline_capable=excluded.offline_capable,
            internet_requirement=excluded.internet_requirement,
            verification_status=excluded.verification_status,
            last_verified_date=excluded.last_verified_date;
        """,
        (
            model.model_id,
            model.name,
            model.task_type,
            model.engine_type,
            model.version,
            model.weights_source,
            model.code_license,
            model.weights_license,
            model.dataset_license,
            model.voice_asset_license,
            model.exact_license_version,
            model.official_license_url,
            model.official_download_url,
            model.commercial_use_status,
            1 if model.attribution_required else 0,
            model.attribution_text,
            model.verification_evidence,
            model.checksum_sha256,
            model.local_path,
            model.min_ram_gb,
            model.min_vram_gb,
            model.recommended_device,
            1 if model.cpu_support else 0,
            1 if model.offline_capable else 0,
            1 if model.internet_requirement else 0,
            model.verification_status,
            model.last_verified_date,
        )
    )
    await db.commit()
    return ModelRegistry(**model.model_dump())


async def get_model(db: aiosqlite.Connection, model_id: str) -> Optional[ModelRegistry]:
    async with db.execute("SELECT * FROM model_registry WHERE model_id = ?;", (model_id,)) as cursor:
        row = await cursor.fetchone()
        if not row:
            return None
        return ModelRegistry(
            model_id=row["model_id"],
            name=row["name"],
            task_type=row["task_type"],
            engine_type=row["engine_type"],
            version=row["version"],
            weights_source=row["weights_source"],
            code_license=row["code_license"],
            weights_license=row["weights_license"],
            dataset_license=row["dataset_license"],
            voice_asset_license=row["voice_asset_license"],
            exact_license_version=row["exact_license_version"],
            official_license_url=row["official_license_url"],
            official_download_url=row["official_download_url"],
            commercial_use_status=row["commercial_use_status"],
            attribution_required=bool(row["attribution_required"]),
            attribution_text=row["attribution_text"],
            verification_evidence=row["verification_evidence"],
            checksum_sha256=row["checksum_sha256"],
            local_path=row["local_path"],
            min_ram_gb=row["min_ram_gb"],
            min_vram_gb=row["min_vram_gb"],
            recommended_device=row["recommended_device"],
            cpu_support=bool(row["cpu_support"]),
            offline_capable=bool(row["offline_capable"]),
            internet_requirement=bool(row["internet_requirement"]),
            verification_status=row["verification_status"],
            last_verified_date=row["last_verified_date"],
        )


async def list_models(db: aiosqlite.Connection) -> List[ModelRegistry]:
    async with db.execute("SELECT * FROM model_registry ORDER BY name ASC;") as cursor:
        rows = await cursor.fetchall()
        return [
            ModelRegistry(
                model_id=row["model_id"],
                name=row["name"],
                task_type=row["task_type"],
                engine_type=row["engine_type"],
                version=row["version"],
                weights_source=row["weights_source"],
                code_license=row["code_license"],
                weights_license=row["weights_license"],
                dataset_license=row["dataset_license"],
                voice_asset_license=row["voice_asset_license"],
                exact_license_version=row["exact_license_version"],
                official_license_url=row["official_license_url"],
                official_download_url=row["official_download_url"],
                commercial_use_status=row["commercial_use_status"],
                attribution_required=bool(row["attribution_required"]),
                attribution_text=row["attribution_text"],
                verification_evidence=row["verification_evidence"],
                checksum_sha256=row["checksum_sha256"],
                local_path=row["local_path"],
                min_ram_gb=row["min_ram_gb"],
                min_vram_gb=row["min_vram_gb"],
                recommended_device=row["recommended_device"],
                cpu_support=bool(row["cpu_support"]),
                offline_capable=bool(row["offline_capable"]),
                internet_requirement=bool(row["internet_requirement"]),
                verification_status=row["verification_status"],
                last_verified_date=row["last_verified_date"],
            )
            for row in rows
        ]


# ==========================================
# System Settings CRUD
# ==========================================
async def get_system_settings(db: aiosqlite.Connection) -> SystemSettings:
    async with db.execute("SELECT * FROM system_settings WHERE id = 'default';") as cursor:
        row = await cursor.fetchone()
        if not row:
            raise RuntimeError("Default system settings record missing")
        return SystemSettings(
            id=row["id"],
            verified_free_models=json.loads(row["verified_free_models"]),
            active_gemini_model=row["active_gemini_model"],
            offline_mode_enabled=bool(row["offline_mode_enabled"]),
            commercial_mode_strict=bool(row["commercial_mode_strict"]),
            updated_at=row["updated_at"],
        )


async def update_system_settings(db: aiosqlite.Connection, updates: Dict[str, Any]) -> SystemSettings:
    now = _utc_now_iso()
    current = await get_system_settings(db)
    
    verified_models = updates.get("verified_free_models", current.verified_free_models)
    if isinstance(verified_models, list):
        verified_models = json.dumps(verified_models)
        
    active_gemini = updates.get("active_gemini_model", current.active_gemini_model)
    offline = 1 if updates.get("offline_mode_enabled", current.offline_mode_enabled) else 0
    strict = 1 if updates.get("commercial_mode_strict", current.commercial_mode_strict) else 0
    
    await db.execute(
        """
        UPDATE system_settings
        SET verified_free_models = ?, active_gemini_model = ?, offline_mode_enabled = ?, commercial_mode_strict = ?, updated_at = ?
        WHERE id = 'default';
        """,
        (verified_models, active_gemini, offline, strict, now)
    )
    await db.commit()
    return await get_system_settings(db)
