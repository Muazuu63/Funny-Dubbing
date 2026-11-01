"""FFmpeg-based audio/video compositor engine."""
from app.config import settings

class CompositorEngine:
    def __init__(self):
        self.ffmpeg_path = settings.resolve_ffmpeg_binary()
        self.ffprobe_path = settings.resolve_ffprobe_binary()
