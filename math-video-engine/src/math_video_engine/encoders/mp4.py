"""High-performance MP4 video encoder streaming directly into FFmpeg."""

from __future__ import annotations
import os
import shutil
import subprocess
from typing import Sequence, Iterator, Union
from PIL import Image


def is_ffmpeg_available() -> bool:
    """Check if ffmpeg executable is installed and reachable via PATH."""
    return shutil.which("ffmpeg") is not None


def encode_mp4(
    frames: Union[Sequence[Image.Image], Iterator[Image.Image]],
    output_path: str,
    fps: int = 30,
    preset: str = "medium",
    crf: int = 18,
) -> str:
    """Encode an image sequence into an H.264 MP4 file via FFmpeg pipe."""
    if not is_ffmpeg_available():
        raise RuntimeError(
            "FFmpeg is not available on PATH. Please install ffmpeg or use 'gif' or 'webp' format."
        )

    frame_iter = iter(frames)
    first_frame = next(frame_iter, None)
    if first_frame is None:
        raise ValueError("Cannot encode empty frame sequence into MP4.")

    width, height = first_frame.size
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "rgba",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", preset,
        "-crf", str(crf),
        "-movflags", "+faststart",
        output_path,
    ]

    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )

    try:
        # Write first frame
        process.stdin.write(first_frame.tobytes())
        # Write remaining frames
        for frame in frame_iter:
            if frame.size != (width, height):
                frame = frame.resize((width, height))
            process.stdin.write(frame.tobytes())
    except (BrokenPipeError, IOError):
        pass
    finally:
        try:
            if process.stdin and not process.stdin.closed:
                process.stdin.close()
        except Exception:
            pass

    stderr_data = b""
    if process.stderr:
        stderr_data = process.stderr.read()
        process.stderr.close()
    process.wait()

    if process.returncode != 0:
        err_msg = stderr_data.decode(errors="replace")
        raise RuntimeError(f"FFmpeg encoding failed with code {process.returncode}: {err_msg}")

    return output_path
