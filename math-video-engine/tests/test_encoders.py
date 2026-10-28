"""Unit tests for video and animation exporters."""

import os
import pytest
from PIL import Image
from math_video_engine.encoders.gif import encode_gif
from math_video_engine.encoders.webp import encode_webp
from math_video_engine.encoders.mp4 import encode_mp4, is_ffmpeg_available
from math_video_engine.encoders.frame_sequence import export_frame_sequence


def create_dummy_frames(count=5, size=(100, 100)):
    return [Image.new("RGBA", size, (i * 40, 50, 100, 255)) for i in range(count)]


def test_encode_gif(tmp_path):
    frames = create_dummy_frames()
    out_file = str(tmp_path / "test.gif")
    result = encode_gif(frames, out_file, fps=10)
    assert os.path.exists(result)
    assert os.path.getsize(result) > 0


def test_encode_webp(tmp_path):
    frames = create_dummy_frames()
    out_file = str(tmp_path / "test.webp")
    result = encode_webp(frames, out_file, fps=10)
    assert os.path.exists(result)
    assert os.path.getsize(result) > 0


def test_export_frame_sequence(tmp_path):
    frames = create_dummy_frames(count=3)
    out_dir = str(tmp_path / "frames")
    result = export_frame_sequence(frames, out_dir, prefix="img")
    assert os.path.exists(result)
    files = sorted(os.listdir(result))
    assert len(files) == 3
    assert files[0] == "img_00001.png"


def test_encode_mp4(tmp_path):
    if not is_ffmpeg_available():
        pytest.skip("FFmpeg not installed")
    frames = create_dummy_frames(count=10, size=(128, 128))
    out_file = str(tmp_path / "test.mp4")
    result = encode_mp4(frames, out_file, fps=10)
    assert os.path.exists(result)
    assert os.path.getsize(result) > 0


def test_empty_frames_error(tmp_path):
    with pytest.raises(ValueError):
        encode_gif([], str(tmp_path / "empty.gif"))
    with pytest.raises(ValueError):
        encode_webp([], str(tmp_path / "empty.webp"))
    if is_ffmpeg_available():
        with pytest.raises(ValueError):
            encode_mp4([], str(tmp_path / "empty.mp4"))
