"""Configuration and global constants for Math Video Engine."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Dict

RESOLUTION_PRESETS: Dict[str, Tuple[int, int]] = {
    "preview": (480, 270),
    "480p": (854, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "1440p": (2560, 1440),
    "4k": (3840, 2160),
}

DEFAULT_FRAME_HEIGHT: float = 8.0
DEFAULT_ASPECT_RATIO: float = 16.0 / 9.0
DEFAULT_FRAME_WIDTH: float = DEFAULT_FRAME_HEIGHT * DEFAULT_ASPECT_RATIO  # ~14.2222
DEFAULT_FPS: int = 30
DEFAULT_BACKGROUND_COLOR: str = "#0f141d"


@dataclass
class RenderConfig:
    """Settings passed to the renderer and video pipeline."""
    width: int = 1280
    height: int = 720
    fps: int = 30
    background_color: str = DEFAULT_BACKGROUND_COLOR
    frame_width: float = DEFAULT_FRAME_WIDTH
    frame_height: float = DEFAULT_FRAME_HEIGHT
    output_dir: str = "output"

    @classmethod
    def from_preset(
        cls,
        preset: str = "720p",
        fps: int = DEFAULT_FPS,
        background_color: str = DEFAULT_BACKGROUND_COLOR,
        output_dir: str = "output"
    ) -> RenderConfig:
        preset_key = preset.lower()
        if preset_key not in RESOLUTION_PRESETS:
            raise ValueError(
                f"Unknown resolution preset '{preset}'. "
                f"Available presets: {list(RESOLUTION_PRESETS.keys())}"
            )
        width, height = RESOLUTION_PRESETS[preset_key]
        return cls(
            width=width,
            height=height,
            fps=fps,
            background_color=background_color,
            output_dir=output_dir,
        )
