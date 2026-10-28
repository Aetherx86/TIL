"""Coordinate systems, axes, and number planes."""

from __future__ import annotations
import numpy as np
from typing import Sequence, Optional, List, Tuple
from math_video_engine.objects.base import MObject, VGroup
from math_video_engine.objects.geometry import Line, Arrow
from math_video_engine.colors import BLUE_D, GRAY_D, GRAY_C, WHITE, GRAY_E


class NumberLine(Line):
    """A 1D axis with tick marks."""

    def __init__(
        self,
        x_min: float = -7.0,
        x_max: float = 7.0,
        unit_size: float = 1.0,
        tick_frequency: float = 1.0,
        tick_size: float = 0.1,
        color: str = WHITE,
        stroke_width: float = 2.0,
        **kwargs
    ):
        start = (x_min, 0.0)
        end = (x_max, 0.0)
        super().__init__(start=start, end=end, color=color, stroke_width=stroke_width, **kwargs)
        self.x_min = x_min
        self.x_max = x_max
        self.unit_size = unit_size
        self.tick_frequency = tick_frequency
        self.tick_size = tick_size

    def get_tick_marks(self) -> List[Line]:
        ticks: List[Line] = []
        x = self.x_min
        while x <= self.x_max + 1e-6:
            ticks.append(Line(
                start=(x, -self.tick_size),
                end=(x, self.tick_size),
                color=self.stroke_color,
                stroke_width=1.5
            ))
            x += self.tick_frequency
        return ticks


class CoordinateAxes(VGroup):
    """X and Y coordinate axes intersecting at the origin."""

    def __init__(
        self,
        x_range: Tuple[float, float, float] = (-7.0, 7.0, 1.0),
        y_range: Tuple[float, float, float] = (-4.0, 4.0, 1.0),
        color: str = GRAY_C,
        stroke_width: float = 2.0,
        include_arrows: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.x_min, self.x_max, self.x_step = x_range
        self.y_min, self.y_max, self.y_step = y_range

        if include_arrows:
            self.x_axis = Arrow(start=(self.x_min, 0.0), end=(self.x_max, 0.0), color=color, stroke_width=stroke_width)
            self.y_axis = Arrow(start=(0.0, self.y_min), end=(0.0, self.y_max), color=color, stroke_width=stroke_width)
        else:
            self.x_axis = Line(start=(self.x_min, 0.0), end=(self.x_max, 0.0), color=color, stroke_width=stroke_width)
            self.y_axis = Line(start=(0.0, self.y_min), end=(0.0, self.y_max), color=color, stroke_width=stroke_width)

        self.add(self.x_axis, self.y_axis)

        # Add tick lines
        x = self.x_min
        while x <= self.x_max + 1e-6:
            if abs(x) > 1e-6:
                self.add(Line(start=(x, -0.08), end=(x, 0.08), color=color, stroke_width=1.5))
            x += self.x_step

        y = self.y_min
        while y <= self.y_max + 1e-6:
            if abs(y) > 1e-6:
                self.add(Line(start=(-0.08, y), end=(0.08, y), color=color, stroke_width=1.5))
            y += self.y_step


class NumberPlane(VGroup):
    """2D Cartesian grid matching the iconic 3Blue1Brown grid layout."""

    def __init__(
        self,
        x_range: Tuple[float, float, float] = (-7.0, 7.0, 1.0),
        y_range: Tuple[float, float, float] = (-4.0, 4.0, 1.0),
        axis_color: str = BLUE_D,
        grid_color: str = "#202a3c",
        sub_grid_color: str = "#161d2a",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.x_min, self.x_max, self.x_step = x_range
        self.y_min, self.y_max, self.y_step = y_range
        self.grid_lines: List[Line] = []

        # Background vertical grid lines
        x = self.x_min
        while x <= self.x_max + 1e-6:
            if abs(x) > 1e-6:
                line = Line(start=(x, self.y_min), end=(x, self.y_max), color=grid_color, stroke_width=1.0)
                self.grid_lines.append(line)
                self.add(line)
            x += self.x_step

        # Background horizontal grid lines
        y = self.y_min
        while y <= self.y_max + 1e-6:
            if abs(y) > 1e-6:
                line = Line(start=(self.x_min, y), end=(self.x_max, y), color=grid_color, stroke_width=1.0)
                self.grid_lines.append(line)
                self.add(line)
            y += self.y_step

        # Main axes
        self.axes = CoordinateAxes(
            x_range=x_range,
            y_range=y_range,
            color=axis_color,
            stroke_width=2.5,
            include_arrows=True
        )
        self.add(self.axes)

    def apply_matrix(self, matrix: np.ndarray) -> NumberPlane:
        """Apply a 2x2 linear transformation matrix to every grid line and axis."""
        mat = np.asarray(matrix, dtype=float)
        for line in self.grid_lines:
            line.start = line.start @ mat.T
            line.end = line.end @ mat.T

        self.axes.x_axis.start = self.axes.x_axis.start @ mat.T
        self.axes.x_axis.end = self.axes.x_axis.end @ mat.T
        self.axes.y_axis.start = self.axes.y_axis.start @ mat.T
        self.axes.y_axis.end = self.axes.y_axis.end @ mat.T
        return self
