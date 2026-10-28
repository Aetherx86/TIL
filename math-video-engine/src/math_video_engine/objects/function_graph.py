"""Function graphs, parametric curves, Riemann sums, and tangents."""

from __future__ import annotations
import numpy as np
from typing import Callable, Sequence, Optional, List, Tuple
from math_video_engine.objects.base import MObject, VGroup
from math_video_engine.objects.geometry import Line, Rectangle
from math_video_engine.colors import BLUE, YELLOW, GREEN, RED, BLUE_E


class ParametricCurve(MObject):
    """A 2D parametric curve t -> (x(t), y(t))."""

    def __init__(
        self,
        func: Callable[[float], Sequence[float]],
        t_range: Tuple[float, float, int] = (0.0, 1.0, 100),
        color: str = BLUE,
        stroke_width: float = 3.0,
        **kwargs
    ):
        super().__init__(stroke_color=color, stroke_width=stroke_width, **kwargs)
        self.func = func
        self.t_min, self.t_max, self.num_samples = t_range
        self.points = self._generate_points()

    def _generate_points(self) -> np.ndarray:
        ts = np.linspace(self.t_min, self.t_max, self.num_samples)
        pts = [self.func(t)[:2] for t in ts]
        return np.array(pts, dtype=float)

    def get_center(self) -> np.ndarray:
        if len(self.points) == 0:
            return np.zeros(2, dtype=float)
        return np.mean(self.points, axis=0)

    def shift(self, vector: Sequence[float]) -> ParametricCurve:
        self.points += np.array(vector[:2], dtype=float)
        return self


class FunctionGraph(ParametricCurve):
    """Graph of a scalar function y = f(x)."""

    def __init__(
        self,
        func: Callable[[float], float],
        x_range: Tuple[float, float, int] = (-5.0, 5.0, 200),
        color: str = BLUE,
        stroke_width: float = 3.0,
        **kwargs
    ):
        x_min, x_max, samples = x_range
        super().__init__(
            func=lambda x: (x, func(x)),
            t_range=(x_min, x_max, samples),
            color=color,
            stroke_width=stroke_width,
            **kwargs
        )
        self.scalar_func = func


class RiemannRectangles(VGroup):
    """Collection of vertical rectangles approximating the integral of f(x)."""

    def __init__(
        self,
        func: Callable[[float], float],
        x_range: Tuple[float, float],
        num_rectangles: int = 10,
        stroke_color: str = BLUE,
        fill_color: str = BLUE_E,
        fill_opacity: float = 0.5,
        sample_point: str = "midpoint",  # "left", "right", "midpoint"
        **kwargs
    ):
        super().__init__(**kwargs)
        self.func = func
        self.x_min, self.x_max = x_range
        self.num_rectangles = max(1, num_rectangles)
        self.rectangles: List[Rectangle] = []

        dx = (self.x_max - self.x_min) / self.num_rectangles
        for i in range(self.num_rectangles):
            x_left = self.x_min + i * dx
            if sample_point == "left":
                x_sample = x_left
            elif sample_point == "right":
                x_sample = x_left + dx
            else:  # midpoint
                x_sample = x_left + 0.5 * dx

            y_val = func(x_sample)
            rect = Rectangle(
                width=dx,
                height=abs(y_val),
                center=(x_left + 0.5 * dx, y_val / 2.0),
                stroke_color=stroke_color,
                stroke_width=1.5,
                fill_color=fill_color,
                fill_opacity=fill_opacity
            )
            self.rectangles.append(rect)
            self.add(rect)


class TangentLine(Line):
    """Local tangent line to a function f(x) at x_0."""

    def __init__(
        self,
        func: Callable[[float], float],
        x_0: float,
        length: float = 3.0,
        dx: float = 1e-5,
        color: str = YELLOW,
        stroke_width: float = 2.5,
        **kwargs
    ):
        y_0 = func(x_0)
        slope = (func(x_0 + dx) - func(x_0 - dx)) / (2.0 * dx)
        # Unit tangent vector
        denom = np.sqrt(1.0 + slope * slope)
        ux, uy = 1.0 / denom, slope / denom
        half_len = length / 2.0
        start = (x_0 - half_len * ux, y_0 - half_len * uy)
        end = (x_0 + half_len * ux, y_0 + half_len * uy)
        super().__init__(start=start, end=end, color=color, stroke_width=stroke_width, **kwargs)
        self.x_0 = x_0
        self.slope = slope
