"""Video and animation exporters package."""

from __future__ import annotations
import os
from typing import Optional
from math_video_engine.scenes.base import Scene
from math_video_engine.encoders.gif import encode_gif
from math_video_engine.encoders.webp import encode_webp
from math_video_engine.encoders.mp4 import encode_mp4, is_ffmpeg_available
from math_video_engine.encoders.frame_sequence import export_frame_sequence


def export_video(
    scene: Scene,
    output_path: Optional[str] = None,
    output_format: str = "mp4",
    fps: Optional[int] = None,
) -> str:
    """Render a Scene instance and export to the requested video/animation format."""
    frame_rate = fps or scene.config.fps
    fmt = output_format.lower().lstrip(".")

    scene_name = scene.__class__.__name__
    if output_path is None:
        os.makedirs(scene.config.output_dir, exist_ok=True)
        if fmt == "frames":
            output_path = os.path.join(scene.config.output_dir, scene_name)
        else:
            output_path = os.path.join(scene.config.output_dir, f"{scene_name}.{fmt}")

    frames = scene.generate_frames(fps=frame_rate)

    if fmt == "mp4":
        if not is_ffmpeg_available():
            # Fall back to animated WebP or GIF if FFmpeg is absent
            fallback_path = os.path.splitext(output_path)[0] + ".gif"
            print(f"Warning: FFmpeg not detected. Falling back to GIF export: {fallback_path}")
            return encode_gif(frames, fallback_path, fps=frame_rate)
        return encode_mp4(frames, output_path, fps=frame_rate)
    elif fmt == "gif":
        return encode_gif(frames, output_path, fps=frame_rate)
    elif fmt == "webp":
        return encode_webp(frames, output_path, fps=frame_rate)
    elif fmt in ("frames", "png", "images"):
        return export_frame_sequence(frames, output_path)
    else:
        raise ValueError(
            f"Unsupported output format: '{output_format}'. "
            "Supported formats: 'mp4', 'gif', 'webp', 'frames'."
        )


__all__ = [
    "encode_gif",
    "encode_webp",
    "encode_mp4",
    "is_ffmpeg_available",
    "export_frame_sequence",
    "export_video",
]
