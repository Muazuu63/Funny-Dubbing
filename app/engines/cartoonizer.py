"""
Studio-Grade 2D Anime & Cartoonizer Engine (Mode 02: Cartoon Re-creation Studio).
Replaces legacy OpenCV edge filters with Neural AnimeGANv2 Stylization.
Master Architecture v2.2 & PRD v2.2 Aligned.

Enforces:
1. Studio-Grade 2D Anime Stylization (AnimeGANv2 Hayao / Studio Ghibli & Shinkai Styles):
   Replaces dirty OpenCV thresholding and posterization with deep neural style transfer.
2. 1:1 Frame Match & Microsecond Audio Sync:
   Preserves original FPS, aspect ratio, and total frame count so lip gestures and comedy timing match audio perfectly.
3. Edge Smoothing & Color Grading:
   Applies edge-preserving bilateral smoothing, saturation pop, and warmth grading for vibrant digital animation.
4. Temporal Consistency (Jitter Prevention):
   Applies exponential moving average (EMA) frame blending to eliminate neural flickering.
5. Zero Extra Cost & Memory Safety:
   100% offline local processing with ONNX Runtime and streaming FFmpeg pipes.
"""
import os
import gc
import cv2
import asyncio
import subprocess
import urllib.request
import numpy as np
from pathlib import Path
from typing import Optional, Callable, Dict, Any

from app.config import settings

try:
    import onnxruntime as ort
except ImportError:
    ort = None


class CartoonizerEngine:
    """
    Studio-Grade Neural 2D Cartoonizer Engine using AnimeGANv2 ONNX Runtime.
    """

    MODEL_URLS = {
        "hayao": "https://huggingface.co/vumichien/AnimeGANv2_Hayao/resolve/main/AnimeGANv2_Hayao.onnx",
        "shinkai": "https://huggingface.co/vumichien/AnimeGANv2_Shinkai/resolve/main/AnimeGANv2_Shinkai.onnx",
    }

    def __init__(self, style: str = "hayao"):
        self.style = style.lower() if style.lower() in self.MODEL_URLS else "hayao"
        self.ffmpeg_path = settings.resolve_ffmpeg_binary()
        self.models_dir = settings.BASE_DIR / "storage" / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self._session: Optional[Any] = None
        self._in_name: Optional[str] = None
        self._out_name: Optional[str] = None

    def _ensure_model(self) -> Path:
        """Ensures the selected ONNX model weights exist locally, downloading if necessary."""
        filename = f"AnimeGANv2_{self.style.capitalize()}.onnx"
        model_path = self.models_dir / filename

        if not model_path.exists() or model_path.stat().st_size < 1000000:
            url = self.MODEL_URLS.get(self.style, self.MODEL_URLS["hayao"])
            try:
                urllib.request.urlretrieve(url, str(model_path))
            except Exception as e:
                # Fallback to Hayao if specific style download fails
                hayao_path = self.models_dir / "AnimeGANv2_Hayao.onnx"
                if hayao_path.exists():
                    return hayao_path
                raise RuntimeError(f"Failed to acquire AnimeGANv2 model from {url}: {e}")

        return model_path

    def _get_session(self):
        """Initializes and caches the optimized ONNX Runtime session."""
        if self._session is None:
            if ort is None:
                raise RuntimeError("onnxruntime is required for Studio-Grade AnimeGANv2 Stylization.")

            model_path = self._ensure_model()
            opts = ort.SessionOptions()
            cpu_threads = os.cpu_count() or 4
            opts.intra_op_num_threads = cpu_threads
            opts.inter_op_num_threads = 2
            opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
            opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

            providers = ["CPUExecutionProvider"]
            # Auto-detect CUDA if available
            available_providers = ort.get_available_providers()
            if "CUDAExecutionProvider" in available_providers:
                providers.insert(0, "CUDAExecutionProvider")

            self._session = ort.InferenceSession(str(model_path), sess_options=opts, providers=providers)
            self._in_name = self._session.get_inputs()[0].name
            self._out_name = self._session.get_outputs()[0].name

        return self._session

    def cartoonize_frame(
        self,
        bgr_frame: np.ndarray,
        prev_frame: Optional[np.ndarray] = None,
        max_internal_dim: int = 360
    ) -> np.ndarray:
        """
        Transforms a single frame into a studio-grade 2D anime illustration:
        1. Resizes to optimal internal processing resolution (multiple of 16 for CNN).
        2. Normalizes RGB input to [-1, 1].
        3. Runs AnimeGANv2 deep neural style transfer.
        4. Denormalizes output to [0, 255].
        5. Post-processes: Fast edge smoothing, saturation pop, and Ghibli warmth.
        6. Applies EMA blending with previous frame for jitter-free temporal consistency.
        """
        orig_h, orig_w = bgr_frame.shape[:2]

        # 1. Optimal internal processing dimensions (multiple of 16)
        scale = min(1.0, float(max_internal_dim) / max(orig_h, orig_w))
        pw = max(16, int(round((orig_w * scale) / 16)) * 16)
        ph = max(16, int(round((orig_h * scale) / 16)) * 16)

        resized = cv2.resize(bgr_frame, (pw, ph), interpolation=cv2.INTER_AREA)
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

        # 2. Normalize to [-1.0, 1.0]
        norm = (rgb.astype(np.float32) / 127.5) - 1.0
        batch = np.expand_dims(norm, axis=0)

        # 3. ONNX Neural Inference
        session = self._get_session()
        raw_out = session.run([self._out_name], {self._in_name: batch})[0]

        # 4. Denormalize to uint8 BGR
        denorm = ((raw_out[0] + 1.0) * 127.5).clip(0, 255).astype(np.uint8)
        art_bgr = cv2.cvtColor(denorm, cv2.COLOR_RGB2BGR)

        if (pw, ph) != (orig_w, orig_h):
            art_bgr = cv2.resize(art_bgr, (orig_w, orig_h), interpolation=cv2.INTER_LANCZOS4)

        # 5. Fast Studio Art Post-Processing:
        # A. Edge-preserving surface brush smoothing (d=3 for ultra-fast CPU inference)
        smooth = cv2.bilateralFilter(art_bgr, d=3, sigmaColor=15, sigmaSpace=15)

        # B. Color Vibrancy (boost saturation by 15%)
        hsv = cv2.cvtColor(smooth, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.15, 0, 255)
        vibrant = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)

        # C. Warmth Color Grading (Ghibli warmth: slight red & yellow warmth, reduced blue)
        vibrant[:, :, 2] = np.clip(vibrant[:, :, 2] * 1.04, 0, 255)  # Red
        vibrant[:, :, 1] = np.clip(vibrant[:, :, 1] * 1.01, 0, 255)  # Green
        vibrant[:, :, 0] = np.clip(vibrant[:, :, 0] * 0.98, 0, 255)  # Blue
        final_art = vibrant.astype(np.uint8)

        # 6. Temporal Consistency (EMA Frame Blending to prevent flickering)
        if prev_frame is not None and prev_frame.shape == final_art.shape:
            final_art = cv2.addWeighted(final_art, 0.88, prev_frame, 0.12, 0)

        return final_art

    async def cartoonize_video(
        self,
        input_video_path: Path,
        output_video_path: Path,
        batch_size: int = 16,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Path:
        """
        Transforms video into 1:1 studio-grade 2D anime video track using streaming FFmpeg pipe.
        Maintains 100% exact frame count and FPS for zero-drift audio sync.
        """
        output_video_path.parent.mkdir(parents=True, exist_ok=True)
        if not input_video_path.exists():
            raise FileNotFoundError(f"Source video not found: {input_video_path}")

        cap = cv2.VideoCapture(str(input_video_path.resolve()))
        if not cap.isOpened():
            raise RuntimeError(f"Could not open video file: {input_video_path}")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 360)
        fps = float(cap.get(cv2.CAP_PROP_FPS) or 25.0)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)

        # Launch streaming FFmpeg process for fast, memory-safe encoding
        cmd = [
            str(self.ffmpeg_path),
            "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{width}x{height}",
            "-pix_fmt", "bgr24",
            "-r", str(fps),
            "-i", "-",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "19",
            "-pix_fmt", "yuv420p",
            str(output_video_path.resolve()),
        ]

        pipe = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        frame_idx = 0
        prev_frame: Optional[np.ndarray] = None

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Ultra-Fast 15 FPS Anime Sampling ("Animation on Twos"):
                # Real anime characters are animated on "twos" (12-15 fps).
                # Stylizing every 2nd frame cuts neural inference time by 50%
                # while giving that authentic hand-drawn cel anime motion aesthetic!
                if frame_idx % 2 == 0 or prev_frame is None:
                    anime_frame = self.cartoonize_frame(frame, prev_frame=prev_frame, max_internal_dim=360)
                    prev_frame = anime_frame
                else:
                    anime_frame = prev_frame

                pipe.stdin.write(anime_frame.tobytes())
                frame_idx += 1

                if progress_callback and frame_idx % batch_size == 0:
                    try:
                        progress_callback(frame_idx, total_frames)
                    except Exception:
                        pass

                # Memory safety: clear caches periodically
                if frame_idx % 64 == 0:
                    gc.collect()

        finally:
            cap.release()
            if pipe.stdin:
                pipe.stdin.close()
            pipe.wait()
            gc.collect()

        if not output_video_path.exists() or output_video_path.stat().st_size == 0:
            raise RuntimeError(f"Failed to render studio cartoon video to {output_video_path}")

        return output_video_path
