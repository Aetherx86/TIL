"""Fundamental geometric primitives and shapes."""

from __future__ import annotations
import math
import numpy as np
from typing import Sequence, Optional, List, Tuple
from math_video_engine.objects.base import MObject
from math_video_engine.colors import WHITE, BLUE, RED, YELLOW


def rotation_matrix_2d(angle: float) -> np.ndarray:
    """Return 2x2 rotation matrix for counter-clockwise rotation by angle (radians)."""
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[c, -s], [s, c]], dtype=float)


class Polygon(MObject):
    """General polygon defined by 2D vertex points."""

    def __init__(self, vertices: Sequence[Sequence[float]], **kwargs):
        super().__init__(**kwargs)
        self.vertices = np.array([v[:2] for v in vertices], dtype=float)

    def get_center(self) -> np.ndarray:
        if len(self.vertices) == 0:
            return np.zeros(2, dtype=float)
        return np.mean(self.vertices, axis=0)

    def shift(self, vector: Sequence[float]) -> Polygon:
        vec = np.array(vector[:2], dtype=float)
        self.vertices += vec
        return self

    def scale(self, factor: float, about_point: Optional[Sequence[float]] = None) -> Polygon:
        ref = self.get_center() if about_point is None else np.array(about_point[:2], dtype=float)
        self.vertices = ref + factor * (self.vertices - ref)
        return self

    def rotate(self, angle: float, about_point: Optional[Sequence[float]] = None) -> Polygon:
        ref = self.get_center() if about_point is None else np.array(about_point[:2], dtype=float)
        rot = rotation_matrix_2d(angle)
        self.vertices = ref + (self.vertices - ref) @ rot.T
        return self


class Dot(MObject):
    """A circular dot positioned at a point."""

    def __init__(
        self,
        point: Sequence[float] = (0.0, 0.0),
        radius: float = 0.08,
        color: str = WHITE,
        **kwargs
    ):
        super().__init__(stroke_color=color, fill_color=color, fill_opacity=1.0, **kwargs)
        self.point = np.array(point[:2], dtype=float)
        self.radius = float(radius)

    def get_center(self) -> np.ndarray:
        return self.point.copy()

    def shift(self, vector: Sequence[float]) -> Dot:
        self.point += np.array(vector[:2], dtype=float)
        return self

    def scale(self, factor: float, about_point: Optional[Sequence[float]] = None) -> Dot:
        self.radius *= factor
        if about_point is not None:
            ref = np.array(about_point[:2], dtype=float)
            self.point = ref + factor * (self.point - ref)
        return self

    def rotate(self, angle: float, about_point: Optional[Sequence[float]] = None) -> Dot:
        if about_point is not None:
            ref = np.array(about_point[:2], dtype=float)
            rot = rotation_matrix_2d(angle)
            self.point = ref + (self.point - ref) @ rot.T
        return self


class Line(MObject):
    """A straight line segment between start and end points."""

    def __init__(
        self,
        start: Sequence[float] = (-1.0, 0.0),
        end: Sequence[float] = (1.0, 0.0),
        color: str = WHITE,
        stroke_width: float = 2.0,
        **kwargs
    ):
        super().__init__(stroke_color=color, stroke_width=stroke_width, **kwargs)
        self.start = np.array(start[:2], dtype=float)
        self.end = np.array(end[:2], dtype=float)

    def get_center(self) -> np.ndarray:
        return (self.start + self.end) / 2.0

    def get_length(self) -> float:
        return float(np.linalg.norm(self.end - self.start))

    def get_unit_vector(self) -> np.ndarray:
        diff = self.end - self.start
        length = np.linalg.norm(diff)
        if length == 0:
            return np.array([1.0, 0.0])
        return diff / length

    def shift(self, vector: Sequence[float]) -> Line:
        vec = np.array(vector[:2], dtype=float)
        self.start += vec
        self.end += vec
        return self

    def scale(self, factor: float, about_point: Optional[Sequence[float]] = None) -> Line:
        ref = self.get_center() if about_point is None else np.array(about_point[:2], dtype=float)
        self.start = ref + factor * (self.start - ref)
        self.end = ref + factor * (self.end - ref)
        return self

    def rotate(self, angle: float, about_point: Optional[Sequence[float]] = None) -> Line:
        ref = self.get_center() if about_point is None else np.array(about_point[:2], dtype=float)
        rot = rotation_matrix_2d(angle)
        self.start = ref + (self.start - ref) @ rot.T
        self.end = ref + (self.end - ref) @ rot.T
        return self


class Arrow(Line):
    """A directed line segment featuring a triangular tip at its end."""

    def __init__(
        self,
        start: Sequence[float] = (0.0, 0.0),
        end: Sequence[float] = (1.0, 0.0),
        tip_length: float = 0.25,
        tip_angle: float = math.pi / 6.0,
        color: str = YELLOW,
        stroke_width: float = 3.0,
        **kwargs
    ):
        super().__init__(start=start, end=end, color=color, stroke_width=stroke_width, **kwargs)
        self.tip_length = tip_length
        self.tip_angle = tip_angle

    def get_tip_points(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Compute the 3 world coordinates forming the arrow tip triangle."""
        tip = self.end
        unit = self.get_unit_vector()
        normal = np.array([-unit[1], unit[0]], dtype=float)
        base = tip - unit * self.tip_length
        half_width = self.tip_length * math.tan(self.tip_angle)
        left = base + normal * half_width
        right = base - normal * half_width
        return tip, left, right


class Rectangle(Polygon):
    """A rectangular polygon oriented horizontally/vertically before rotation."""

    def __init__(
        self,
        width: float = 2.0,
        height: float = 1.0,
        center: Sequence[float] = (0.0, 0.0),
        stroke_color: str = WHITE,
        stroke_width: float = 2.0,
        fill_color: Optional[str] = None,
        fill_opacity: float = 0.0,
        **kwargs
    ):
        cx, cy = center[:2]
        hw, hh = width / 2.0, height / 2.0
        vertices = [
            [cx - hw, cy - hh],
            [cx + hw, cy - hh],
            [cx + hw, cy + hh],
            [cx - hw, cy + hh],
        ]
        super().__init__(
            vertices=vertices,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            **kwargs
        )
        self.width = width
        self.height = height


class Square(Rectangle):
    """A rectangle with equal width and height."""

    def __init__(self, side_length: float = 2.0, **kwargs):
        super().__init__(width=side_length, height=side_length, **kwargs)


class Circle(MObject):
    """A circle defined by center point and radius."""

    def __init__(
        self,
        radius: float = 1.0,
        center: Sequence[float] = (0.0, 0.0),
        color: str = RED,
        stroke_width: float = 2.5,
        fill_color: Optional[str] = None,
        fill_opacity: float = 0.0,
        **kwargs
    ):
        super().__init__(
            stroke_color=color,
            stroke_width=stroke_width,
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            **kwargs
        )
        self.center = np.array(center[:2], dtype=float)
        self.radius = float(radius)

    def get_center(self) -> np.ndarray:
        return self.center.copy()

    def shift(self, vector: Sequence[float]) -> Circle:
        self.center += np.array(vector[:2], dtype=float)
        return self

    def scale(self, factor: float, about_point: Optional[Sequence[float]] = None) -> Circle:
        self.radius *= factor
        if about_point is not None:
            ref = np.array(about_point[:2], dtype=float)
            self.center = ref + factor * (self.center - ref)
        return self

    def rotate(self, angle: float, about_point: Optional[Sequence[float]] = None) -> Circle:
        if about_point is not None:
            ref = np.array(about_point[:2], dtype=float)
            rot = rotation_matrix_2d(angle)
            self.center = ref + (self.center - ref) @ rot.T
        return self


class Arc(MObject):
    """A circular arc tracing an angle from start_angle."""

    def __init__(
        self,
        radius: float = 1.0,
        start_angle: float = 0.0,
        angle: float = math.pi / 2.0,
        center: Sequence[float] = (0.0, 0.0),
        color: str = WHITE,
        stroke_width: float = 2.0,
        num_points: int = 32,
        **kwargs
    ):
        super().__init__(stroke_color=color, stroke_width=stroke_width, **kwargs)
        self.radius = radius
        self.start_angle = start_angle
        self.angle = angle
        self.center = np.array(center[:2], dtype=float)
        self.num_points = max(2, num_points)

    def get_points(self) -> np.ndarray:
        angles = np.linspace(self.start_angle, self.start_angle + self.angle, self.num_points)
        xs = self.center[0] + self.radius * np.cos(angles)
        ys = self.center[1] + self.radius * np.sin(angles)
        return np.column_stack([xs, ys])

    def get_center(self) -> np.ndarray:
        return self.center.copy()

    def shift(self, vector: Sequence[float]) -> Arc:
        self.center += np.array(vector[:2], dtype=float)
        return self
