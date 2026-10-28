"""Animation base classes and core transitions."""

from __future__ import annotations
import copy
import numpy as np
from typing import Optional, Callable
from math_video_engine.objects.base import MObject
from math_video_engine.easing import smooth, RateFunc


class Animation:
    """Base class defining an animation applied to a MObject over time."""

    def __init__(
        self,
        mobject: MObject,
        run_time: float = 1.0,
        rate_func: RateFunc = smooth,
    ):
        if run_time <= 0.0:
            raise ValueError("Animation run_time must be strictly positive.")
        self.mobject = mobject
        self.run_time = float(run_time)
        self.rate_func = rate_func
        self.starting_mobject: Optional[MObject] = None

    def begin(self) -> None:
        """Capture the initial state of the mobject prior to animation start."""
        self.starting_mobject = self.mobject.copy()

    def update(self, raw_alpha: float) -> None:
        """Apply interpolated animation progress."""
        alpha = self.rate_func(max(0.0, min(1.0, raw_alpha)))
        self.interpolate(alpha)

    def interpolate(self, alpha: float) -> None:
        """Override in subclasses to compute the visual state at progress alpha."""
        pass

    def finish(self) -> None:
        """Ensure the animation settles exactly in its final state."""
        self.update(1.0)


class Wait(Animation):
    """Null animation representing a pause in the timeline."""

    def __init__(self, run_time: float = 1.0):
        dummy_mobject = MObject()
        dummy_mobject.visible = False
        super().__init__(mobject=dummy_mobject, run_time=run_time, rate_func=lambda t: t)

    def interpolate(self, alpha: float) -> None:
        pass


class FadeIn(Animation):
    """Fade a mobject into view by ramping opacity from 0 to target."""

    def __init__(self, mobject: MObject, run_time: float = 1.0, rate_func: RateFunc = smooth):
        super().__init__(mobject=mobject, run_time=run_time, rate_func=rate_func)
        self.target_stroke_opacity = mobject.stroke_opacity
        self.target_fill_opacity = mobject.fill_opacity

    def begin(self) -> None:
        super().begin()
        self.mobject.stroke_opacity = 0.0
        self.mobject.fill_opacity = 0.0
        self.mobject.visible = True

    def interpolate(self, alpha: float) -> None:
        self.mobject.stroke_opacity = self.target_stroke_opacity * alpha
        self.mobject.fill_opacity = self.target_fill_opacity * alpha


class FadeOut(Animation):
    """Fade a mobject out of view by ramping opacity to 0."""

    def __init__(self, mobject: MObject, run_time: float = 1.0, rate_func: RateFunc = smooth):
        super().__init__(mobject=mobject, run_time=run_time, rate_func=rate_func)
        self.start_stroke_opacity = mobject.stroke_opacity
        self.start_fill_opacity = mobject.fill_opacity

    def interpolate(self, alpha: float) -> None:
        self.mobject.stroke_opacity = self.start_stroke_opacity * (1.0 - alpha)
        self.mobject.fill_opacity = self.start_fill_opacity * (1.0 - alpha)

    def finish(self) -> None:
        super().finish()
        self.mobject.visible = False
