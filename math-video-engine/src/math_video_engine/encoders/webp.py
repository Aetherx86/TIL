"""Animated WebP encoder using Pillow."""

from __future__ import annotations
import os
from typing import Sequence, Iterator, Union
from PIL import Image


def encode_webp(
    frames: Union[Sequence[Image.Image], Iterator[Image.Image]],
    output_path: str,
    fps: int = 30,
    lossless: bool = False,
    quality: int = 85,
) -> str:
    """Encode an image sequence into an animated WebP file."""
    frame_list = list(frames) if not isinstance(frames, list) else frames
    if not frame_list:
        raise ValueError("Cannot encode empty frame sequence into WebP.")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    frame_duration_ms = int(round(1000.0 / fps))

    frame_list[0].save(
        output_path,
        format="WEBP",
        save_all=True,
        append_images=frame_list[1:],
        duration=frame_duration_ms,
        loop=0,
        lossless=lossless,
        quality=quality,
    )
    return output_path
