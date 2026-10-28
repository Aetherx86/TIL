"""Animated GIF encoder using Pillow."""

from __future__ import annotations
import os
from typing import Sequence, Iterator, Union
from PIL import Image


def encode_gif(
    frames: Union[Sequence[Image.Image], Iterator[Image.Image]],
    output_path: str,
    fps: int = 30,
    optimize: bool = True,
) -> str:
    """Encode an image sequence into an animated GIF file."""
    frame_list = list(frames) if not isinstance(frames, list) else frames
    if not frame_list:
        raise ValueError("Cannot encode empty frame sequence into GIF.")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    frame_duration_ms = int(round(1000.0 / fps))

    # Convert RGBA to RGB with palette quantization for GIF format
    paletted_frames = [
        f.convert("RGB").quantize(colors=256, method=Image.Quantize.MEDIANCUT)
        for f in frame_list
    ]

    paletted_frames[0].save(
        output_path,
        save_all=True,
        append_images=paletted_frames[1:],
        duration=frame_duration_ms,
        loop=0,
        optimize=optimize,
    )
    return output_path
