"""Export frames as numbered image sequence."""

from __future__ import annotations
import os
from typing import Sequence, Iterator, Union
from PIL import Image


def export_frame_sequence(
    frames: Union[Sequence[Image.Image], Iterator[Image.Image]],
    output_dir: str,
    prefix: str = "frame",
    extension: str = "png",
) -> str:
    """Save frames into output_dir as prefix_0001.png, prefix_0002.png, ..."""
    os.makedirs(output_dir, exist_ok=True)
    for idx, frame in enumerate(frames, start=1):
        filename = f"{prefix}_{idx:05d}.{extension}"
        filepath = os.path.join(output_dir, filename)
        frame.save(filepath)
    return output_dir
