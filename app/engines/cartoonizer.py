"""
Local Visual Cartoonizer Engine (Mode 02: Cartoon Re-creation Studio).
Master Architecture v2.2 & PRD v2.2 Aligned.

Key Principles:
1. 1:1 Frame Match & Timeline Preservation:
   Maintains identical FPS, aspect ratio, and total frame count so lip movement and gestures
   remain in 100% microsecond frame-sync with audio.
2. Vibrant 2D Anime & Cel-Shaded Aesthetics:
   Applies edge-preserving bilateral smoothing, cel-shading color quantization,
   and clean cartoon ink contours.
3. Memory & Resource Safety:
   Processes frames in streams/batches with explicit garbage collection to prevent VRAM/RAM spikes.
4. Zero Extra Cost:
   100% offline local processing without cloud APIs or token costs.
"""
import os
import gc
import cv2
import asyncio
import subprocess
import numpy as np
from pathlib import Path
from typing import Optional, Callable, Dict, Any

from app.config import settings


class CartoonizerEngine:
    def __init__(self):
        self.ffmpeg_path = settings.resolve_ffmpeg_binary()

    @staticmethod
    def cartoonize_frame(bgr_frame: np.ndarray) -> np.ndarray:
        """
        Converts a real-world photo/video frame into a high-quality 2D cartoon / anime aesthetic:
        - Bilateral filtering smooths skin and textures while preserving sharp boundaries.
        - Cel-shading color quantization simulates hand-drawn comic frames.
        - Saturation enhancement pops vibrant animated colors.
        - Adaptive thresholding creates clean cartoon ink outline edges.
        """
        h, w = bgr_frame.shape[:2]

        # 1. Edge-preserving surface smoothing (removes realistic skin pores, textures)
        smooth = cv2.bilateralFilter(bgr_frame, d=7, sigmaColor=50, sigmaSpace=50)

        # 2. Cel-shading / comic color quantization
        quantized = (smooth // 22) * 22 + 11

        # 3. Enhance saturation & vibrancy for animated cartoon look
        hsv = cv2.cvtColor(quantized, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.25, 0, 255)  # boost saturation
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.05, 0, 255)  # boost brightness slightly
        vibrant_bgr = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

        # 4. Clean anime ink contour lines
        gray = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(
            gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 3
        )
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        # 5. Composite cel-shaded colors with ink edges
        cartoon = cv2.bitwise_and(vibrant_bgr, edges_bgr)
        return cartoon

    async def cartoonize_video(
        self,
        input_video_path: Path,
        output_video_path: Path,
        batch_size: int = 16,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Path:
        """
        Transforms full video into 1:1 frame-accurate cartoon video track using streaming FFmpeg pipe.
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
            "-crf", "20",
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
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                cartoon_frame = self.cartoonize_frame(frame)
                pipe.stdin.write(cartoon_frame.tobytes())
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
            raise RuntimeError(f"Failed to render cartoon video to {output_video_path}")

        return output_video_path
