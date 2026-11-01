"""Durable step checkpointing system."""
from pathlib import Path

class Checkpointer:
    def __init__(self, checkpoints_dir: Path):
        self.checkpoints_dir = checkpoints_dir
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
