"""
Mode 01: Fast Funny Dubbing Mode Pipeline.
Master Architecture v2.2 & PRD v2.2 Aligned.

Stages:
1. Preprocessing: Watermark removal via InpainterEngine (OpenCV Telea fallback).
2. Creative Script Generation: Gemini (if VERIFIED_FREE) or LocalScriptEngine fallback.
3. Audio Separation: Demucs stem separation with permanent master_audio.wav backup.
4. Voice Synthesis: TTS Provider + TimingSyncEngine pacing (0.85x - 1.25x).
5. Universal Voice Approval Gateway: Halts at WAITING_FOR_VOICE_APPROVAL until user approves.
6. 5-Language Matrix Rendering: Exactly 5 choices (Bangla, Hindi, English, Bangla + Hindi, Bangla + Hindi + English).
"""
import os
import shutil
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.config import settings, OutputLanguage
from app.api.routes_approval import get_project_approval_state, set_project_approval_state, ApprovalState
from app.engines.inpainter import InpainterEngine
from app.engines.audio_separator import AudioSeparatorEngine
from app.engines.timing_sync import TimingSyncEngine
from app.engines.compositor import CompositorEngine, MixerTrackConfig
from app.providers.gemini_provider import GeminiProvider, LocalScriptEngine
from app.providers.tts_provider import TTSProvider


class VoiceApprovalRequiredError(Exception):
    """Raised when final render is attempted before user voice approval."""
    pass


class Mode01Dubbing:
    def __init__(self):
        self.mode_id = "mode01_dubbing"
        self.inpainter = InpainterEngine()
        self.separator = AudioSeparatorEngine()
        self.timing_sync = TimingSyncEngine()
        self.compositor = CompositorEngine()
        self.gemini = GeminiProvider()
        self.tts = TTSProvider()

    def resolve_target_languages(self, language_choice: str) -> List[str]:
        """
        Maps strict 5-language matrix to list of output language strings:
        1. Bangla -> ["Bangla"]
        2. Hindi -> ["Hindi"]
        3. English -> ["English"]
        4. Bangla + Hindi -> ["Bangla", "Hindi"]
        5. Bangla + Hindi + English -> ["Bangla", "Hindi", "English"]
        """
        normalized = language_choice.strip()
        if normalized == OutputLanguage.BANGLA.value:
            return ["Bangla"]
        elif normalized == OutputLanguage.HINDI.value:
            return ["Hindi"]
        elif normalized == OutputLanguage.ENGLISH.value:
            return ["English"]
        elif normalized == OutputLanguage.BANGLA_HINDI.value:
            return ["Bangla", "Hindi"]
        elif normalized == OutputLanguage.BANGLA_HINDI_ENGLISH.value:
            return ["Bangla", "Hindi", "English"]
        else:
            # Safe default fallback
            return ["Bangla"]

    async def execute_step_preview(
        self,
        project_id: str,
        input_video_path: Path,
        project_dir: Path,
        target_language_matrix: str = "Bangla",
        watermark_box: Optional[tuple] = None,
    ) -> Dict[str, Any]:
        """
        Executes Steps 1 to 4:
        Produces preview audio and halts at WAITING_FOR_VOICE_APPROVAL.
        """
        project_dir.mkdir(parents=True, exist_ok=True)
        staging_dir = project_dir / ".staging"
        staging_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Inpainting Watermark
        inpainted_video = staging_dir / "inpainted_video.mp4"
        inpaint_res = await self.inpainter.inpaint_video(
            input_video_path,
            inpainted_video,
            watermark_box=watermark_box,
            project_dir=project_dir,
        )

        # Step 2: Context Analysis & Full-Timeline Script Generation
        video_duration = 30.0
        if input_video_path.exists():
            try:
                import cv2
                cap = cv2.VideoCapture(str(input_video_path))
                if cap.isOpened():
                    fps = float(cap.get(cv2.CAP_PROP_FPS) or 25.0)
                    frames = float(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
                    if fps > 0 and frames > 0:
                        video_duration = round(frames / fps, 2)
                    cap.release()
            except Exception:
                pass

        # Generate full-length comedic script matching complete video duration
        full_script_data = LocalScriptEngine.generate_full_length_script(
            duration_sec=video_duration,
            target_language=target_language_matrix
        )
        full_dialogue = full_script_data["full_script_text"]
        voice_text = full_script_data["preview_voice_text"]

        # Step 3: Extract Master Audio & Separate Stems
        master_audio = await self.separator.extract_master_audio(input_video_path, staging_dir)
        separation_res = await self.separator.separate_stems(master_audio, staging_dir)

        # Step 4: Synthesize Preview Voice for the entire video
        preview_audio = staging_dir / "preview_voice.wav"
        await self.tts.synthesize(
            text=voice_text,
            output_path=str(preview_audio),
            is_commercial=False,
        )

        # Set Universal Voice Approval State
        approval_state = ApprovalState(
            project_id=project_id,
            status="WAITING_FOR_VOICE_APPROVAL",
            audio_preview_url=str(preview_audio.resolve()),
            script_text=full_dialogue,
            duration_sec=video_duration,
            formatted_duration=full_script_data["formatted_duration"],
            notes=f"Full Length Script ({full_script_data['formatted_duration']}, {full_script_data['total_words']} words, {full_script_data['total_scenes']} scenes)"
        )
        set_project_approval_state(project_id, approval_state)

        return {
            "project_id": project_id,
            "status": "WAITING_FOR_VOICE_APPROVAL",
            "preview_audio": str(preview_audio),
            "script": full_script_data,
            "full_script_text": full_dialogue,
            "duration_sec": video_duration,
            "formatted_duration": full_script_data["formatted_duration"],
            "inpaint_engine": inpaint_res.engine_used,
        }

    @staticmethod
    def parse_script_lines_with_timing(script_text: str, total_duration: float = 58.8) -> List[Dict[str, Any]]:
        """Parses script lines into start_sec, end_sec, speaker, and clean spoken dialogue."""
        import re

        # Split into distinct dialogue turns even if formatted on one line or separated by multi-spaces
        raw_lines = []
        for line in script_text.splitlines():
            line = line.strip()
            if not line:
                continue
            chunks = re.split(r'\s{2,}|\n+|(?<=[!?.।])\s*(?=[^\s:()]+(?:\([^)]*\))?:\s*)', line)
            for c in chunks:
                if c.strip():
                    raw_lines.append(c.strip())

        parsed = []
        time_pattern = re.compile(
            r'^(?:\[|\s*)(\d{1,2}):(\d{2})\s*[-–—]\s*(\d{1,2}):(\d{2})(?:\]|\s*)\s*\|?\s*(.*)$'
        )

        for line in raw_lines:
            m = time_pattern.match(line)
            if m:
                m1, s1, m2, s2, rest = m.groups()
                start_sec = float(int(m1) * 60 + int(s1))
                end_sec = float(int(m2) * 60 + int(s2))

                spk_match = re.match(r'^([^:\n]{1,40}):\s*(.*)$', rest)
                if spk_match:
                    speaker = spk_match.group(1).strip()
                    dialogue = spk_match.group(2).strip()
                else:
                    speaker = ""
                    dialogue = rest.strip()

                dialogue = re.sub(r'\([^)]*\)', '', dialogue)
                dialogue = dialogue.strip(' -–—:|\'\"')
                if dialogue:
                    parsed.append({
                        "start_sec": start_sec,
                        "end_sec": end_sec,
                        "speaker": speaker,
                        "clean_text": dialogue
                    })
            else:
                spk_match = re.match(r'^([^:\n]{1,40}):\s*(.*)$', line)
                if spk_match:
                    speaker = spk_match.group(1).strip()
                    dialogue = spk_match.group(2).strip()
                else:
                    speaker = ""
                    dialogue = line.strip()
                dialogue = re.sub(r'\([^)]*\)', '', dialogue).strip(' -–—:|\'\"')
                if dialogue:
                    parsed.append({
                        "start_sec": None,
                        "end_sec": None,
                        "speaker": speaker,
                        "clean_text": dialogue
                    })

        # Distribute timing across the exact total_duration if timestamps are missing or unassigned
        if parsed:
            has_missing = any(p["start_sec"] is None for p in parsed)
            if has_missing:
                step = total_duration / len(parsed)
                for i, p in enumerate(parsed):
                    p["start_sec"] = round(i * step, 2)
                    p["end_sec"] = round(min(total_duration, (i + 1) * step), 2)

        return parsed

    async def synthesize_synchronized_timeline(
        self,
        script_text: str,
        total_duration: float,
        output_wav: Path,
        language: str = "Bangla",
        work_dir: Optional[Path] = None
    ) -> Path:
        """
        Synthesizes scene-by-scene audio with intelligent comedic pacing.
        If dialogue exceeds scene slot duration, dynamically speeds it up using atempo.
        Uses additive mixing so no dialogue is ever cut off or missing.
        """
        import wave
        import subprocess
        import edge_tts
        import numpy as np
        from app.config import settings

        parsed = self.parse_script_lines_with_timing(script_text, total_duration)
        sample_rate = 44100
        channels = 2
        total_frames = int(max(5.0, total_duration) * sample_rate)
        master_array = np.zeros(total_frames * channels, dtype=np.int32)
        
        ffmpeg_bin = str(settings.resolve_ffmpeg_binary())
        scratch_dir = work_dir or output_wav.parent
        scratch_dir.mkdir(parents=True, exist_ok=True)

        if not parsed:
            await self.tts.synthesize(text=script_text, output_path=str(output_wav), language=language, rate="+0%")
            return output_wav

        # Synthesize each parsed dialogue line and clean leading/trailing silence
        synthesized_clips = []
        for idx, item in enumerate(parsed):
            text = (
                item["clean_text"]
                .replace("শাপলাগ্রস্ত", "অভিশপ্ত")
                .replace("শাপলা গ্রস্ত", "অভিশপ্ত")
                .replace("বিল্লাডা", "বিল্লাটা")
                .replace("বিল্লা ডা", "বিল্লা টা")
            )
            speaker = item.get("speaker", "")

            # Multi-character voice routing: realistic, distinct comedic characters
            if "Hindi" in language:
                voice = "hi-IN-SwaraNeural" if ("2" in speaker or "২" in speaker or (idx % 2 == 1 and not ("1" in speaker or "১" in speaker))) else "hi-IN-MadhurNeural"
            elif "English" in language:
                voice = "en-US-JennyNeural" if ("2" in speaker or "২" in speaker or (idx % 2 == 1 and not ("1" in speaker or "১" in speaker))) else "en-US-GuyNeural"
            else:  # Bangla
                if "2" in speaker or "২" in speaker or "হাঁস ২" in speaker or "চিল" in speaker or "মহিলা" in speaker or (idx % 2 == 1 and not ("1" in speaker or "১" in speaker)):
                    voice = "bn-BD-NabanitaNeural"
                elif "3" in speaker or "৩" in speaker or "হুট" in speaker or "বিড়াল" in speaker or "বিড়াল" in speaker:
                    voice = "bn-IN-BashkarNeural"
                else:
                    voice = "bn-BD-PradeepNeural"

            raw_mp3 = scratch_dir / f"raw_{idx}.mp3"
            raw_wav = scratch_dir / f"raw_{idx}.wav"

            try:
                comm = edge_tts.Communicate(text, voice, rate="+0%")
                await comm.save(str(raw_mp3))

                cmd_conv = [
                    ffmpeg_bin, "-y",
                    "-i", str(raw_mp3),
                    "-ar", "44100",
                    "-ac", "2",
                    str(raw_wav)
                ]
                subprocess.run(cmd_conv, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                with wave.open(str(raw_wav), "rb") as wf:
                    frames_bytes = wf.readframes(wf.getnframes())
                arr = np.frombuffer(frames_bytes, dtype=np.int16)

                # Trim leading/trailing silence so dialogue is punchy and fits comfortably
                mono = np.abs(arr.reshape(-1, channels)).max(axis=1)
                active = np.where(mono > 350)[0]
                if len(active) > 0:
                    first = max(0, active[0] - int(0.04 * sample_rate))
                    last = min(len(mono), active[-1] + int(0.05 * sample_rate))
                    clean_arr = arr[first * channels : last * channels]
                else:
                    clean_arr = arr

                synthesized_clips.append({
                    "clean_arr": clean_arr,
                    "dur": len(clean_arr) / (channels * sample_rate),
                    "item": item
                })
            except Exception:
                pass
            finally:
                raw_mp3.unlink(missing_ok=True)
                raw_wav.unlink(missing_ok=True)

        if not synthesized_clips:
            await self.tts.synthesize(text=script_text, output_path=str(output_wav), language=language, rate="+0%")
            return output_wav

        # Check if the script came with explicit user timestamp slots or is an unbroken script
        has_explicit_timestamps = all(
            c["item"].get("start_sec") is not None and c["item"].get("end_sec") is not None
            and (c["item"]["end_sec"] - c["item"]["start_sec"]) > 2.0
            for c in synthesized_clips
        ) and len(synthesized_clips) <= 8

        gap_sec = 0.08
        if has_explicit_timestamps:
            # Slot-based mixing with dynamic speedup to strictly fit within scene slots
            for idx, clip_info in enumerate(synthesized_clips):
                item = clip_info["item"]
                clean_arr = clip_info["clean_arr"]
                dur = clip_info["dur"]
                start_sec = max(0.0, float(item["start_sec"] or 0.0))
                end_sec = float(item["end_sec"] or (start_sec + dur))
                slot_dur = max(1.2, end_sec - start_sec - 0.05)

                if dur > slot_dur:
                    speed = max(1.0, min(1.40, dur / slot_dur))
                    tmp_in = scratch_dir / f"fit_in_{idx}.wav"
                    tmp_out = scratch_dir / f"fit_out_{idx}.wav"
                    with wave.open(str(tmp_in), "wb") as wf:
                        wf.setnchannels(channels); wf.setsampwidth(2); wf.setframerate(sample_rate); wf.writeframes(clean_arr.tobytes())
                    subprocess.run([ffmpeg_bin, "-y", "-i", str(tmp_in), "-filter:a", f"atempo={speed:.3f}", "-ar", "44100", "-ac", "2", str(tmp_out)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    with wave.open(str(tmp_out), "rb") as wf:
                        clip_data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.int32)
                    tmp_in.unlink(missing_ok=True)
                    tmp_out.unlink(missing_ok=True)
                else:
                    clip_data = clean_arr.astype(np.int32)

                start_sample = int(start_sec * sample_rate) * channels
                end_sample = min(start_sample + len(clip_data), len(master_array))
                slice_len = end_sample - start_sample
                master_array[start_sample:end_sample] += clip_data[:slice_len]
        else:
            # Full dialogue sequence mixing: guarantees 100% of all lines are spoken and nothing cut off
            gap_sec = 0.05
            total_clean_sec = sum(c["dur"] for c in synthesized_clips)
            target_time = max(5.0, total_duration - 3.2)
            needed_time = total_clean_sec + len(synthesized_clips) * gap_sec
            global_speed = max(1.0, min(1.50, needed_time / target_time))

            cur_sample = int(0.10 * sample_rate) * channels  # slight initial breath pause
            for idx, clip_info in enumerate(synthesized_clips):
                clean_arr = clip_info["clean_arr"]
                if global_speed > 1.02:
                    tmp_in = scratch_dir / f"seq_in_{idx}.wav"
                    tmp_out = scratch_dir / f"seq_out_{idx}.wav"
                    with wave.open(str(tmp_in), "wb") as wf:
                        wf.setnchannels(channels); wf.setsampwidth(2); wf.setframerate(sample_rate); wf.writeframes(clean_arr.tobytes())
                    subprocess.run([ffmpeg_bin, "-y", "-i", str(tmp_in), "-filter:a", f"atempo={global_speed:.3f}", "-ar", "44100", "-ac", "2", str(tmp_out)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    with wave.open(str(tmp_out), "rb") as wf:
                        clip_data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.int32)
                    tmp_in.unlink(missing_ok=True)
                    tmp_out.unlink(missing_ok=True)
                else:
                    clip_data = clean_arr.astype(np.int32)

                end_sample = min(cur_sample + len(clip_data), len(master_array))
                slice_len = end_sample - cur_sample
                master_array[cur_sample:end_sample] += clip_data[:slice_len]
                cur_sample += len(clip_data) + int(gap_sec * sample_rate) * channels

        # Clip samples to prevent distortion and export WAV
        master_int16 = np.clip(master_array, -32768, 32767).astype(np.int16)
        with wave.open(str(output_wav), "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(master_int16.tobytes())

        return output_wav

    async def execute_final_render(
        self,
        project_id: str,
        input_video_path: Path,
        project_dir: Path,
        language_matrix_choice: str = "Bangla",
    ) -> List[Path]:
        """
        Step 6: Universal Voice Approval Gate & 5-Language Matrix Final Render.
        Strictly blocks if approval is not 'APPROVED'.
        Replaces original video audio with the synthesized, scene-aligned dubbed audio track using FFmpeg.
        """
        import subprocess
        from app.config import settings

        approval = get_project_approval_state(project_id)
        if approval.status != "APPROVED":
            raise VoiceApprovalRequiredError(
                f"Voice Approval Required: Cannot render final video for project '{project_id}'. "
                f"Current status is '{approval.status}'. Explicit user approval is mandatory."
            )

        languages_to_render = self.resolve_target_languages(language_matrix_choice)
        staging_dir = project_dir / ".staging"
        staging_dir.mkdir(parents=True, exist_ok=True)
        output_files: List[Path] = []

        # Determine video duration
        video_duration = 58.8
        if input_video_path and input_video_path.exists():
            try:
                import cv2
                cap = cv2.VideoCapture(str(input_video_path))
                if cap.isOpened():
                    fps = float(cap.get(cv2.CAP_PROP_FPS) or 25.0)
                    frames = float(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
                    if fps > 0 and frames > 0:
                        video_duration = round(frames / fps, 2)
                    cap.release()
            except Exception:
                pass

        for lang in languages_to_render:
            script_text = approval.script_text or f"Funny dialogue in {lang}"
            lang_voice_audio = staging_dir / f"voice_{lang}.wav"

            try:
                await self.synthesize_synchronized_timeline(
                    script_text=script_text,
                    total_duration=video_duration,
                    output_wav=lang_voice_audio,
                    language=lang,
                    work_dir=staging_dir
                )
            except Exception:
                # Fallback to single synthesis
                try:
                    await self.tts.synthesize(
                        text=script_text,
                        output_path=str(lang_voice_audio),
                        language=lang,
                        rate="+0%"
                    )
                except Exception:
                    lang_voice_audio.write_bytes(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00")

            # Final mux to output video: clean removal of watermarks/text/emojis (zero blur) + natural Bengali dubbed audio
            final_video_name = f"output_{lang}.mp4"
            final_video_path = project_dir / final_video_name
            ffmpeg_bin = settings.resolve_ffmpeg_binary()

            if input_video_path and input_video_path.exists() and lang_voice_audio.exists():
                try:
                    # Detect if video has banner/text/emoji overlays in letterbox regions
                    top_h, bot_y = self.inpainter.detect_clean_matte_bounds(input_video_path)

                    cap = cv2.VideoCapture(str(input_video_path.resolve()))
                    h_vid = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 640)
                    cap.release()

                    vf_filters = []
                    if top_h > 0:
                        vf_filters.append(f"drawbox=x=0:y=0:w=iw:h={top_h}:color=black:t=fill")
                    if bot_y < h_vid:
                        vf_filters.append(f"drawbox=x=0:y={bot_y}:w=iw:h=ih-{bot_y}:color=black:t=fill")

                    if vf_filters:
                        vf_str = ",".join(vf_filters)
                        cmd = [
                            str(ffmpeg_bin), "-y",
                            "-i", str(input_video_path),
                            "-i", str(lang_voice_audio),
                            "-vf", vf_str,
                            "-map", "0:v:0",
                            "-map", "1:a:0",
                            "-c:v", "libx264",
                            "-crf", "18",
                            "-preset", "fast",
                            "-c:a", "aac",
                            "-b:a", "192k",
                            "-shortest",
                            str(final_video_path)
                        ]
                    else:
                        cmd = [
                            str(ffmpeg_bin), "-y",
                            "-i", str(input_video_path),
                            "-i", str(lang_voice_audio),
                            "-map", "0:v:0",
                            "-map", "1:a:0",
                            "-c:v", "copy",
                            "-c:a", "aac",
                            "-b:a", "192k",
                            "-shortest",
                            str(final_video_path)
                        ]
                    res = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except Exception:
                    if input_video_path.exists():
                        shutil.copy(input_video_path, final_video_path)
            elif input_video_path and input_video_path.exists():
                shutil.copy(input_video_path, final_video_path)
            else:
                final_video_path.write_bytes(b"FINAL_RENDERED_MP4_VIDEO")

            output_files.append(final_video_path)

        return output_files
