"""Inpainting engine interface (LaMa optional engine wrapper)."""

class InpainterEngine:
    def __init__(self):
        self.name = "LaMa"

    def is_available(self) -> bool:
        return False
