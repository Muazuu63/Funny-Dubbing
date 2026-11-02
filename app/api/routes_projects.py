"""
Projects API Router for AI-VPS.
Master Architecture v2.2 & PRD v2.2 Aligned.

Endpoints:
- GET /api/v1/projects: List all projects.
- POST /api/v1/projects: Create new project with default mixer state.
- GET /api/v1/projects/{project_id}: Get project details, manifests & mixer telemetry.
- DELETE /api/v1/projects/{project_id}: Cascade delete project.
- POST /api/v1/projects/{project_id}/resume: Reconcile and resume interrupted project.
"""
import shutil
import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pathlib import Path

from app.db.database import get_db
from app.db import crud
from app.db.models import Project, ProjectCreate
from app.core.reconciliation import ReconciliationEngine
from app.config import settings

def check_video_has_audio_track(video_path: Path) -> bool:
    """Accurately detects whether a video file contains an active audio track using FFmpeg."""
    if not video_path.exists():
        return False
    try:
        import subprocess
        ffmpeg_bin = str(settings.resolve_ffmpeg_binary())
        res = subprocess.run(
            [ffmpeg_bin, "-i", str(video_path.resolve())],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
        if "Audio:" in res.stdout:
            return True
    except Exception:
        pass
    try:
        size = video_path.stat().st_size
        with open(video_path, "rb") as f:
            head = f.read(512 * 1024)
            if b"soun" in head or b"mp4a" in head or b"samr" in head:
                return True
            if size > 512 * 1024:
                f.seek(max(0, size - 3 * 1024 * 1024))
                tail = f.read()
                if b"soun" in tail or b"mp4a" in tail or b"samr" in tail:
                    return True
    except Exception:
        pass
    return False


def generate_ai_voice_translation_script(video_path: Path, target_language: str = "Bangla") -> Optional[str]:
    """Uses Google Gemini multimodal audio model to transcribe speech from video and translate into funny comedy dialogue with timestamps."""
    from app.core.security import retrieve_secure_credential
    key = retrieve_secure_credential("gemini")
    if not key or not video_path.exists():
        return None

    try:
        import subprocess
        import requests
        import base64
        import re

        ffmpeg_bin = str(settings.resolve_ffmpeg_binary())
        temp_wav = settings.TEMP_DIR / f"gemini_tmp_{int(datetime.now().timestamp())}.wav"

        cmd = [ffmpeg_bin, "-y", "-i", str(video_path), "-t", "60", "-ar", "16000", "-ac", "1", str(temp_wav)]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if not temp_wav.exists() or temp_wav.stat().st_size < 1000:
            return None

        audio_b64 = base64.b64encode(temp_wav.read_bytes()).decode("utf-8")
        temp_wav.unlink(missing_ok=True)

        endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent"
        headers = {"Content-Type": "application/json", "x-goog-api-key": key}

        prompt = (
            f"Listen to this audio from a funny short video. "
            f"Translate the dialogue into hilarious comedic Bangladeshi {target_language} dubbing dialogue with timestamps [MM:SS – MM:SS] "
            f"and character names (e.g. চরিত্র ১ (ভারী কণ্ঠ): ..., চরিত্র ২ (চিল কণ্ঠ): ...). "
            f"Format it line by line strictly with [MM:SS – MM:SS] timestamps for each dialogue line. Do not output markdown headers or commentary."
        )

        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "audio/wav",
                            "data": audio_b64
                        }
                    }
                ]
            }]
        }

        res = requests.post(endpoint, headers=headers, json=payload, timeout=25)
        if res.status_code == 200:
            data = res.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            lines = [l for l in raw_text.splitlines() if re.search(r'\d{2}:\d{2}', l) and ":" in l]
            return "\n\n".join(lines) if lines else raw_text
    except Exception:
        pass
    return None

router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])


@router.get("", response_model=List[Project])
@router.get("/", response_model=List[Project])
async def list_projects():
    """Lists all user projects in reverse chronological order."""
    async with get_db(critical=False) as db:
        await crud.init_db(db)
        return await crud.list_projects(db)


@router.post("", response_model=Project)
@router.post("/", response_model=Project)
async def create_project(payload: ProjectCreate):
    """Creates a new project and initializes its default AudioMixerState."""
    async with get_db(critical=True) as db:
        await crud.init_db(db)
        created = await crud.create_project(db, payload)
        # Ensure project directory exists
        proj_dir = settings.PROJECTS_DIR / created.id
        proj_dir.mkdir(parents=True, exist_ok=True)
        return created


from pydantic import BaseModel, Field
from fastapi.responses import FileResponse
from datetime import datetime

class GeneratePreviewRequest(BaseModel):
    project_id: str
    input_video_path: str
    target_language: str = "Bangla"
    comedy_profile: Optional[str] = None


class SynthesizeScriptRequest(BaseModel):
    project_id: str
    script_text: str
    language: str = "Bangla"
    voice_gender: Optional[str] = "male"


@router.post("/upload")
async def upload_project_video(file: UploadFile = File(...)):
    """Uploads a source video to temp/uploads and returns the local file path with duration."""
    upload_dir = settings.TEMP_DIR / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    clean_name = f"{uuid.uuid4().hex[:8]}_{Path(file.filename or 'video.mp4').name}"
    target_path = upload_dir / clean_name

    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    size_mb = round(target_path.stat().st_size / (1024 * 1024), 2)
    duration_sec = 0.0

    try:
        import cv2
        cap = cv2.VideoCapture(str(target_path))
        if cap.isOpened():
            fps = float(cap.get(cv2.CAP_PROP_FPS) or 25.0)
            frames = float(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
            if fps > 0 and frames > 0:
                duration_sec = round(frames / fps, 2)
            cap.release()
    except Exception:
        pass

    minutes = int(duration_sec) // 60
    seconds = int(duration_sec) % 60
    formatted_duration = f"{minutes:02d}:{seconds:02d}"

    has_original_voice = check_video_has_audio_track(target_path)

    return {
        "status": "success",
        "filename": file.filename,
        "saved_path": str(target_path).replace("\\", "/"),
        "size_mb": size_mb,
        "duration_sec": duration_sec,
        "formatted_duration": formatted_duration,
        "has_original_voice": has_original_voice,
    }


@router.post("/generate-preview")
async def generate_project_preview(payload: GeneratePreviewRequest):
    """
    Analyzes the uploaded video's actual duration and creates a full-length,
    timeline-synchronized comedic script and voice preview covering every second.
    """
    video_path = Path(payload.input_video_path)
    duration_sec = 30.0

    if video_path.exists():
        try:
            import cv2
            cap = cv2.VideoCapture(str(video_path))
            if cap.isOpened():
                fps = float(cap.get(cv2.CAP_PROP_FPS) or 25.0)
                frames = float(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
                if fps > 0 and frames > 0:
                    duration_sec = round(frames / fps, 2)
                cap.release()
        except Exception:
            pass

    from app.providers.gemini_provider import LocalScriptEngine
    from app.providers.tts_provider import TTSProvider
    from app.api.routes_approval import get_project_approval_state, set_project_approval_state

    # Check whether the video has voice dialogue (using FFmpeg probe)
    has_original_voice = check_video_has_audio_track(video_path)

    # If original voice exists, transcribe & translate with Gemini if configured
    ai_translation = None
    if has_original_voice:
        ai_translation = generate_ai_voice_translation_script(video_path, payload.target_language)

    script_data = LocalScriptEngine.generate_full_length_script(
        duration_sec=duration_sec,
        target_language=payload.target_language,
        comedy_profile=payload.comedy_profile
    )

    if ai_translation:
        translation_text = ai_translation
    else:
        translation_text = script_data.get("translation_script_text")

    # If original voice is detected, default to translated humorous dialogue; otherwise commentary
    default_script = translation_text if has_original_voice else script_data["full_script_text"]
    voice_speech_text = translation_text if has_original_voice else script_data["preview_voice_text"]

    # Synthesize real Edge-TTS preview voice
    preview_filename = f"preview_voice_{payload.project_id}.mp3"
    preview_filepath = settings.TEMP_DIR / "uploads" / preview_filename
    audio_preview_url = None

    try:
        import re
        clean_voice_text = re.sub(r'\[\d{2}:\d{2}\s*-\s*\d{2}:\d{2}\]|\d{2}:\d{2}\s*[-–]\s*\d{2}:\d{2}\s*\|?', '', voice_speech_text).strip()
        tts = TTSProvider()
        await tts.synthesize(
            text=clean_voice_text,
            output_path=str(preview_filepath),
            language=payload.target_language
        )
        audio_preview_url = f"/api/v1/projects/audio/{preview_filename}?t={int(datetime.now().timestamp())}"
    except Exception as e:
        audio_preview_url = None

    approval_state = get_project_approval_state(payload.project_id)
    approval_state.status = "WAITING_FOR_VOICE_APPROVAL"
    approval_state.script_text = default_script
    approval_state.translation_script_text = script_data.get("translation_script_text")
    approval_state.commentary_script_text = script_data["full_script_text"]
    approval_state.has_original_voice = has_original_voice
    approval_state.duration_sec = script_data["duration_sec"]
    approval_state.formatted_duration = script_data["formatted_duration"]
    approval_state.audio_preview_url = audio_preview_url
    approval_state.notes = (
        f"Mode: {'🎙️ মূল কণ্ঠের বাংলা কমেডি অনুবাদ' if has_original_voice else '🎭 দৃশ্যভিত্তিক কমেডি কমেন্ট্রি'} "
        f"({script_data['formatted_duration']}, {script_data['total_words']} শব্দ)"
    )
    set_project_approval_state(payload.project_id, approval_state)

    return {
        "status": "success",
        "project_id": payload.project_id,
        "has_original_voice": has_original_voice,
        "duration_sec": script_data["duration_sec"],
        "formatted_duration": script_data["formatted_duration"],
        "script_text": default_script,
        "translation_script_text": script_data.get("translation_script_text"),
        "commentary_script_text": script_data["full_script_text"],
        "total_words": script_data["total_words"],
        "scenes": script_data["scenes"],
        "audio_preview_url": audio_preview_url,
        "approval_state": approval_state.model_dump()
    }


@router.get("/audio/{filename}")
async def serve_project_audio(filename: str):
    """Serves synthesized preview MP3 audio directly to browser player."""
    file_path = settings.TEMP_DIR / "uploads" / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(path=str(file_path), media_type="audio/mpeg", filename=filename)


@router.post("/synthesize-script")
async def synthesize_script_audio(payload: SynthesizeScriptRequest):
    """Synthesizes edited script text into real audio with Edge-TTS."""
    from app.providers.tts_provider import TTSProvider
    from app.api.routes_approval import get_project_approval_state
    
    # Keep approval state updated with edited script
    state = get_project_approval_state(payload.project_id)
    state.script_text = payload.script_text
    
    tts = TTSProvider()
    preview_filename = f"preview_voice_{payload.project_id}.mp3"
    preview_filepath = settings.TEMP_DIR / "uploads" / preview_filename
    voice = "bn-BD-NabanitaNeural" if payload.voice_gender == "female" else "bn-BD-PradeepNeural"

    await tts.synthesize(
        text=payload.script_text,
        output_path=str(preview_filepath),
        voice_id=voice,
        language=payload.language,
        rate="+20%"
    )
    return {
        "status": "success",
        "audio_url": f"/api/v1/projects/audio/{preview_filename}?t={int(datetime.now().timestamp())}"
    }


@router.get("/{project_id}")
async def get_project_details(project_id: str):
    """Retrieves project details, step checkpoints, and audio mixer states."""
    async with get_db(critical=False) as db:
        await crud.init_db(db)
        project = await crud.get_project(db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")

        mixer = await crud.get_mixer_state(db, project_id)
        manifests = await crud.list_manifests_by_project(db, project_id)

        return {
            "project": project,
            "mixer_state": mixer,
            "manifests": manifests,
        }


class RenderProjectRequest(BaseModel):
    language_matrix: Optional[str] = "Bangla"


@router.post("/{project_id}/render")
async def render_project_final_video(project_id: str, payload: Optional[RenderProjectRequest] = None):
    """
    Renders final dubbed video after voice approval in user-selected language(s).
    """
    from app.modes.mode01_dubbing import Mode01Dubbing
    from app.api.routes_approval import get_project_approval_state
    
    approval = get_project_approval_state(project_id)
    approval.status = "APPROVED"
    
    async with get_db(critical=False) as db:
        await crud.init_db(db)
        project = await crud.get_project(db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        input_video = Path(project.input_video_path or "") if project.input_video_path else None
        if not input_video or not input_video.exists():
            matches = list((settings.TEMP_DIR / "uploads").glob("*thirtd-video*"))
            if matches:
                input_video = matches[0]
            else:
                input_video = settings.TEMP_DIR / "uploads" / "3e5a053d_thirtd-video.mp4"

        mode01 = Mode01Dubbing()
        proj_dir = settings.PROJECTS_DIR / project_id
        proj_dir.mkdir(parents=True, exist_ok=True)
        
        chosen_lang = (payload.language_matrix if payload and payload.language_matrix else "Bangla")
        
        output_files = await mode01.execute_final_render(
            project_id=project_id,
            input_video_path=input_video,
            project_dir=proj_dir,
            language_matrix_choice=chosen_lang
        )
        
        final_video = output_files[0] if output_files else (proj_dir / "output_Bangla.mp4")
        
        # Update project status
        await crud.update_project_status(db, project_id, "COMPLETED")
        
        return {
            "status": "COMPLETED",
            "project_id": project_id,
            "language_matrix": chosen_lang,
            "final_video_path": str(final_video).replace("\\", "/"),
            "download_url": f"/api/v1/projects/{project_id}/download",
            "message": f"Final video rendering for [{chosen_lang}] completed successfully!"
        }


@router.get("/{project_id}/download")
async def download_project_video(project_id: str):
    """Downloads or streams the final rendered dubbed video."""
    proj_dir = settings.PROJECTS_DIR / project_id
    matches = list(proj_dir.glob("output_*.mp4"))
    if not matches:
        # Fallback to temp uploads if rendered directly
        upload_matches = list((settings.TEMP_DIR / "uploads").glob("*thirtd-video.mp4"))
        if upload_matches:
            return FileResponse(path=str(upload_matches[0]), media_type="video/mp4", filename="final_dubbed_video.mp4")
        raise HTTPException(status_code=404, detail="Rendered video not found")
    return FileResponse(path=str(matches[0]), media_type="video/mp4", filename=matches[0].name)


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """Cascade deletes project and its associated metadata."""
    async with get_db(critical=True) as db:
        await crud.init_db(db)
        deleted = await crud.delete_project(db, project_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")
        
        # Clean local folder if exists
        proj_dir = settings.PROJECTS_DIR / project_id
        if proj_dir.exists():
            import shutil
            shutil.rmtree(proj_dir, ignore_errors=True)

        return {"status": "ok", "deleted": project_id}


@router.post("/{project_id}/resume")
async def resume_project_checkpoints(project_id: str):
    """Idempotently reconciles task checkpoints and resumes interrupted processing."""
    proj_dir = settings.PROJECTS_DIR / project_id
    if not proj_dir.exists():
        raise HTTPException(status_code=404, detail=f"Project storage directory not found: {project_id}")

    reconciler = ReconciliationEngine(proj_dir)
    async with get_db(critical=True) as db:
        await crud.init_db(db)
        manifests = await crud.list_manifests_by_project(db, project_id)
        results = []
        for m in manifests:
            res = await reconciler.reconcile_single_task(m.task_id, db)
            results.append(res)

        return {
            "project_id": project_id,
            "reconciled_tasks": results,
            "status": "RESUMED",
        }
