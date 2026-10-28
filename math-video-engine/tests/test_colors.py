"""Unit tests for color manipulation and gradients."""

import pytest
from math_video_engine.colors import (
    hex_to_rgb, hex_to_rgba, rgb_to_hex, interpolate_color, color_gradient,
    WHITE, BLACK, RED, BLUE
)


def test_hex_to_rgb_standard():
    assert hex_to_rgb("#FFFFFF") == (255, 255, 255)
    assert hex_to_rgb("#000000") == (0, 0, 0)
    assert hex_to_rgb("#FF0000") == (255, 0, 0)


def test_hex_to_rgb_short():
    assert hex_to_rgb("#FFF") == (255, 255, 255)
    assert hex_to_rgb("#000") == (0, 0, 0)


def test_hex_to_rgb_invalid():
    with pytest.raises(ValueError):
        hex_to_rgb("invalid_hex")


def test_hex_to_rgba_opacity():
    assert hex_to_rgba("#FFFFFF", opacity=1.0) == (255, 255, 255, 255)
    assert hex_to_rgba("#FFFFFF", opacity=0.0) == (255, 255, 255, 0)
    assert hex_to_rgba("#FFFFFF", opacity=0.5) == (255, 255, 255, 128)


def test_rgb_to_hex():
    assert rgb_to_hex(255, 255, 255) == "#FFFFFF"
    assert rgb_to_hex(0, 0, 0) == "#000000"


def test_interpolate_color():
    mid = interpolate_color("#000000", "#FFFFFF", 0.5)
    assert mid == "#808080"


def test_color_gradient():
    grad = color_gradient([BLACK, WHITE], length=5)
    assert len(grad) == 5
    assert grad[0] == BLACK
    assert grad[-1] == WHITE

    # Edge cases
    assert color_gradient([RED], 3) == [RED, RED, RED]
    assert color_gradient([RED, BLUE], 0) == []
    assert color_gradient([RED, BLUE], 1) == [RED]
