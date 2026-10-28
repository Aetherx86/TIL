"""Creation and transformation morph animations."""

from __future__ import annotations
import numpy as np
from typing import Optional
from math_video_engine.animations.base import Animation
from math_video_engine.objects.base import MObject
from math_video_engine.objects.geometry import Line, Polygon, Circle, Dot
from math_video_engine.objects.function_graph import ParametricCurve
from math_video_engine.easing import smooth, RateFunc


class Create(Animation):
    """Draw a mathematical object into the scene over time."""

    def __init__(self, mobject: MObject, run_time: float = 1.0, rate_func: RateFunc = smooth):
        super().__init__(mobject=mobject, run_time=run_time, rate_func=rate_func)

    def begin(self) -> None:
        super().begin()
        self.mobject.visible = True
        if isinstance(self.mobject, Line):
            self.orig_start = self.mobject.start.copy()
            self.orig_end = self.mobject.end.copy()
            self.mobject.end = self.orig_start.copy()
        elif isinstance(self.mobject, ParametricCurve):
            self.orig_points = self.mobject.points.copy()
            self.mobject.points = self.orig_points[:1].copy()
        else:
            self.orig_stroke_op = self.mobject.stroke_opacity
            self.orig_fill_op = self.mobject.fill_opacity
            self.mobject.stroke_opacity = 0.0
            self.mobject.fill_opacity = 0.0

    def interpolate(self, alpha: float) -> None:
        if isinstance(self.mobject, Line):
            self.mobject.end = self.orig_start + alpha * (self.orig_end - self.orig_start)
        elif isinstance(self.mobject, ParametricCurve):
            num_pts = max(1, int(round(alpha * len(self.orig_points))))
            self.mobject.points = self.orig_points[:num_pts]
        else:
            self.mobject.stroke_opacity = self.orig_stroke_op * alpha
            self.mobject.fill_opacity = self.orig_fill_op * alpha

    def finish(self) -> None:
        if isinstance(self.mobject, Line):
            self.mobject.start = self.orig_start.copy()
            self.mobject.end = self.orig_end.copy()
        elif isinstance(self.mobject, ParametricCurve):
            self.mobject.points = self.orig_points.copy()
        else:
            self.mobject.stroke_opacity = self.orig_stroke_op
            self.mobject.fill_opacity = self.orig_fill_op
        self.mobject.visible = True


class Transform(Animation):
    """Morph one mathematical object into another."""

    def __init__(self, source: MObject, target: MObject, run_time: float = 1.0, rate_func: RateFunc = smooth):
        super().__init__(mobject=source, run_time=run_time, rate_func=rate_func)
        self.target = target

    def begin(self) -> None:
        super().begin()
        self.source_copy = self.mobject.copy()

    def interpolate(self, alpha: float) -> None:
        # Interpolate centers
        s_c = self.source_copy.get_center()
        t_c = self.target.get_center()
        curr_c = s_c + alpha * (t_c - s_c)
        self.mobject.move_to(curr_c)

        # Interpolate opacity
        self.mobject.stroke_opacity = (1.0 - alpha) * self.source_copy.stroke_opacity + alpha * self.target.stroke_opacity
        self.mobject.fill_opacity = (1.0 - alpha) * self.source_copy.fill_opacity + alpha * self.target.fill_opacity
