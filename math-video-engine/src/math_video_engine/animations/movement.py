"""Movement, translation, scaling, and rotation animations."""

from __future__ import annotations
import numpy as np
from typing import Sequence, Optional
from math_video_engine.animations.base import Animation
from math_video_engine.objects.base import MObject
from math_video_engine.easing import smooth, RateFunc


class Shift(Animation):
    """Translate a mobject by a displacement vector."""

    def __init__(
        self,
        mobject: MObject,
        vector: Sequence[float],
        run_time: float = 1.0,
        rate_func: RateFunc = smooth,
    ):
        super().__init__(mobject=mobject, run_time=run_time, rate_func=rate_func)
        self.vector = np.array(vector[:2], dtype=float)
        self.last_alpha = 0.0

    def begin(self) -> None:
        super().begin()
        self.last_alpha = 0.0

    def interpolate(self, alpha: float) -> None:
        d_alpha = alpha - self.last_alpha
        self.mobject.shift(d_alpha * self.vector)
        self.last_alpha = alpha


class Rotate(Animation):
    """Rotate a mobject by an angle (radians)."""

    def __init__(
        self,
        mobject: MObject,
        angle: float,
        about_point: Optional[Sequence[float]] = None,
        run_time: float = 1.0,
        rate_func: RateFunc = smooth,
    ):
        super().__init__(mobject=mobject, run_time=run_time, rate_func=rate_func)
        self.angle = angle
        self.about_point = about_point
        self.last_alpha = 0.0

    def begin(self) -> None:
        super().begin()
        self.last_alpha = 0.0

    def interpolate(self, alpha: float) -> None:
        d_alpha = alpha - self.last_alpha
        self.mobject.rotate(d_alpha * self.angle, about_point=self.about_point)
        self.last_alpha = alpha


class Scale(Animation):
    """Scale a mobject by a multiplicative factor."""

    def __init__(
        self,
        mobject: MObject,
        scale_factor: float,
        about_point: Optional[Sequence[float]] = None,
        run_time: float = 1.0,
        rate_func: RateFunc = smooth,
    ):
        super().__init__(mobject=mobject, run_time=run_time, rate_func=rate_func)
        self.scale_factor = scale_factor
        self.about_point = about_point
        self.last_alpha = 0.0

    def begin(self) -> None:
        super().begin()
        self.last_alpha = 0.0

    def interpolate(self, alpha: float) -> None:
        # Scale incrementally
        target_scale = 1.0 + alpha * (self.scale_factor - 1.0)
        prev_scale = 1.0 + self.last_alpha * (self.scale_factor - 1.0)
        step = target_scale / prev_scale if prev_scale != 0 else 1.0
        self.mobject.scale(step, about_point=self.about_point)
        self.last_alpha = alpha
