"""Unit tests for Renderer rasterization."""

from PIL import Image
from math_video_engine.config import RenderConfig
from math_video_engine.camera import Camera
from math_video_engine.renderer import Renderer
from math_video_engine.objects.geometry import Dot, Line, Rectangle, Circle
from math_video_engine.objects.text import Text
from math_video_engine.colors import BLUE, RED, YELLOW


def test_renderer_output_dimensions():
    config = RenderConfig.from_preset("preview")
    cam = Camera(pixel_width=config.width, pixel_height=config.height)
    renderer = Renderer(cam, config)

    dot = Dot(point=(0.0, 0.0), color=RED)
    line = Line(start=(-2.0, 0.0), end=(2.0, 0.0), color=BLUE)
    rect = Rectangle(width=2.0, height=1.0, fill_color=YELLOW, fill_opacity=0.5)
    txt = Text("Test", point=(0.0, 1.0))

    frame = renderer.render_frame([dot, line, rect, txt])
    assert isinstance(frame, Image.Image)
    assert frame.size == (config.width, config.height)
    assert frame.mode == "RGBA"


def test_renderer_z_index_sorting():
    config = RenderConfig.from_preset("preview")
    cam = Camera(pixel_width=config.width, pixel_height=config.height)
    renderer = Renderer(cam, config)

    m1 = Dot(z_index=10)
    m2 = Dot(z_index=2)
    m3 = Dot(z_index=5)

    sorted_objs = renderer.flatten_mobjects([m1, m2, m3])
    assert [m.z_index for m in sorted_objs] == [2, 5, 10]
