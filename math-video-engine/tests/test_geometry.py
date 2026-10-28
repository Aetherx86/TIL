"""Unit tests for geometric MObjects and affine operations."""

import numpy as np
import pytest
from math_video_engine.objects.geometry import Dot, Line, Arrow, Rectangle, Square, Circle, Polygon
from math_video_engine.objects.base import VGroup
from math_video_engine.objects.vector import Vector


def test_dot_shift():
    d = Dot(point=(1.0, 2.0))
    d.shift((2.0, -1.0))
    assert np.allclose(d.get_center(), [3.0, 1.0])


def test_line_length():
    line = Line(start=(0.0, 0.0), end=(3.0, 4.0))
    assert pytest.approx(line.get_length()) == 5.0
    assert np.allclose(line.get_center(), [1.5, 2.0])


def test_arrow_tip_points():
    arrow = Arrow(start=(0.0, 0.0), end=(2.0, 0.0), tip_length=0.4)
    tip, left, right = arrow.get_tip_points()
    assert np.allclose(tip, [2.0, 0.0])
    assert left[0] < tip[0]
    assert right[0] < tip[0]
    assert left[1] > 0
    assert right[1] < 0


def test_rectangle_and_square():
    rect = Rectangle(width=4.0, height=2.0, center=(0.0, 0.0))
    assert np.allclose(rect.get_center(), [0.0, 0.0])
    sq = Square(side_length=3.0, center=(1.0, 1.0))
    assert np.allclose(sq.get_center(), [1.0, 1.0])


def test_circle_scale():
    c = Circle(radius=1.5, center=(0.0, 0.0))
    c.scale(2.0)
    assert c.radius == 3.0


def test_vgroup_composition():
    d1 = Dot(point=(0.0, 0.0))
    d2 = Dot(point=(2.0, 2.0))
    group = VGroup(d1, d2)
    assert len(group) == 2
    assert np.allclose(group.get_center(), [1.0, 1.0])

    group.shift((1.0, 1.0))
    assert np.allclose(d1.get_center(), [1.0, 1.0])
    assert np.allclose(d2.get_center(), [3.0, 3.0])


def test_vector_apply_matrix():
    v = Vector(coords=(1.0, 0.0))
    # 90 degree counter-clockwise rotation matrix: [[0, -1], [1, 0]]
    rot90 = np.array([[0.0, -1.0], [1.0, 0.0]])
    v.apply_matrix(rot90)
    assert np.allclose(v.coords, [0.0, 1.0], atol=1e-5)
