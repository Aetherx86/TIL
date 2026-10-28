"""Unit tests for Camera coordinate mappings and projections."""

import numpy as np
import pytest
from math_video_engine.camera import Camera


def test_camera_initialization():
    cam = Camera(pixel_width=1280, pixel_height=720, frame_width=14.2222, frame_height=8.0)
    assert cam.pixel_width == 1280
    assert cam.pixel_height == 720
    assert np.isclose(cam.frame_center, [0.0, 0.0]).all()


def test_camera_world_to_pixel_center():
    cam = Camera(pixel_width=1280, pixel_height=720, frame_width=16.0, frame_height=9.0)
    # Origin (0, 0) should map to center pixel (640, 360)
    px, py = cam.world_to_pixel((0.0, 0.0))
    assert px == 640
    assert py == 360


def test_camera_invertibility():
    cam = Camera(pixel_width=1280, pixel_height=720, frame_width=14.0, frame_height=8.0)
    test_points = [(0.0, 0.0), (3.5, 2.0), (-5.0, 1.2), (2.1, -3.2)]
    for pt in test_points:
        px, py = cam.world_to_pixel(pt)
        recovered = cam.pixel_to_world((px, py))
        assert np.allclose(pt, recovered, atol=0.05)


def test_camera_pan():
    cam = Camera(pixel_width=1280, pixel_height=720, frame_width=16.0, frame_height=9.0)
    cam.set_frame_center((2.0, 1.0))
    px, py = cam.world_to_pixel((2.0, 1.0))
    assert px == 640
    assert py == 360


def test_camera_zoom():
    cam = Camera(pixel_width=1280, pixel_height=720, frame_width=16.0, frame_height=8.0)
    cam.zoom(2.0)
    assert cam.frame_width == 8.0
    assert cam.frame_height == 4.0

    with pytest.raises(ValueError):
        cam.zoom(-1.0)
