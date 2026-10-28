"""Base Mathematical Object (MObject) and grouping constructs."""

from __future__ import annotations
import copy
import numpy as np
from typing import List, Callable, Optional, Sequence, Union, Tuple
from math_video_engine.colors import WHITE, GRAY, hex_to_rgba


class MObject:
    """Base class for all mathematical visual objects in a scene."""

    def __init__(
        self,
        stroke_color: str = WHITE,
        stroke_width: float = 2.0,
        stroke_opacity: float = 1.0,
        fill_color: Optional[str] = None,
        fill_opacity: float = 0.0,
        z_index: int = 0,
    ):
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.stroke_opacity = stroke_opacity
        self.fill_color = fill_color
        self.fill_opacity = fill_opacity
        self.z_index = z_index
        self.visible = True
        self.updaters: List[Callable[[MObject, float], None]] = []

    def get_center(self) -> np.ndarray:
        """Return the centroid of the object in world coordinates."""
        return np.zeros(2, dtype=float)

    def shift(self, vector: Sequence[float]) -> MObject:
        """Translate the object in world coordinates."""
        return self

    def scale(self, factor: float, about_point: Optional[Sequence[float]] = None) -> MObject:
        """Scale the object relative to a center point."""
        return self

    def rotate(self, angle: float, about_point: Optional[Sequence[float]] = None) -> MObject:
        """Rotate the object counter-clockwise by angle (radians)."""
        return self

    def move_to(self, point: Sequence[float]) -> MObject:
        """Translate object so its center matches target point."""
        current_center = self.get_center()
        target = np.array(point[:2], dtype=float)
        return self.shift(target - current_center)

    def set_color(self, color: str) -> MObject:
        """Set primary stroke color."""
        self.stroke_color = color
        return self

    def set_fill(self, color: str, opacity: float = 1.0) -> MObject:
        """Set fill color and opacity."""
        self.fill_color = color
        self.fill_opacity = opacity
        return self

    def set_stroke(self, color: Optional[str] = None, width: Optional[float] = None, opacity: Optional[float] = None) -> MObject:
        """Configure stroke parameters."""
        if color is not None:
            self.stroke_color = color
        if width is not None:
            self.stroke_width = width
        if opacity is not None:
            self.stroke_opacity = opacity
        return self

    def add_updater(self, updater: Callable[[MObject, float], None]) -> MObject:
        """Attach a function that executes on every timeline step with signature (mobject, dt)."""
        self.updaters.append(updater)
        return self

    def remove_updater(self, updater: Callable[[MObject, float], None]) -> MObject:
        """Remove a previously attached updater."""
        if updater in self.updaters:
            self.updaters.remove(updater)
        return self

    def clear_updaters(self) -> MObject:
        """Remove all updaters from this object."""
        self.updaters.clear()
        return self

    def update(self, dt: float) -> None:
        """Apply all active updaters."""
        for updater in list(self.updaters):
            updater(self, dt)

    def copy(self) -> MObject:
        """Return a deep copy of the object."""
        return copy.deepcopy(self)


class VGroup(MObject):
    """A collection of MObjects treated as a single composite object."""

    def __init__(self, *submobjects: MObject, **kwargs):
        super().__init__(**kwargs)
        self.submobjects: List[MObject] = list(submobjects)

    def add(self, *mobjects: MObject) -> VGroup:
        """Add sub-objects to the group."""
        for m in mobjects:
            if m not in self.submobjects:
                self.submobjects.append(m)
        return self

    def remove(self, *mobjects: MObject) -> VGroup:
        """Remove sub-objects from the group."""
        for m in mobjects:
            if m in self.submobjects:
                self.submobjects.remove(m)
        return self

    def __len__(self) -> int:
        return len(self.submobjects)

    def __getitem__(self, index: int) -> MObject:
        return self.submobjects[index]

    def __iter__(self):
        return iter(self.submobjects)

    def get_center(self) -> np.ndarray:
        if not self.submobjects:
            return np.zeros(2, dtype=float)
        centers = [m.get_center() for m in self.submobjects]
        return np.mean(centers, axis=0)

    def shift(self, vector: Sequence[float]) -> VGroup:
        for m in self.submobjects:
            m.shift(vector)
        return self

    def scale(self, factor: float, about_point: Optional[Sequence[float]] = None) -> VGroup:
        ref = self.get_center() if about_point is None else np.array(about_point[:2], dtype=float)
        for m in self.submobjects:
            m.scale(factor, about_point=ref)
        return self

    def rotate(self, angle: float, about_point: Optional[Sequence[float]] = None) -> VGroup:
        ref = self.get_center() if about_point is None else np.array(about_point[:2], dtype=float)
        for m in self.submobjects:
            m.rotate(angle, about_point=ref)
        return self

    def set_color(self, color: str) -> VGroup:
        super().set_color(color)
        for m in self.submobjects:
            m.set_color(color)
        return self

    def set_stroke(self, color: Optional[str] = None, width: Optional[float] = None, opacity: Optional[float] = None) -> VGroup:
        super().set_stroke(color, width, opacity)
        for m in self.submobjects:
            m.set_stroke(color, width, opacity)
        return self

    def set_fill(self, color: str, opacity: float = 1.0) -> VGroup:
        super().set_fill(color, opacity)
        for m in self.submobjects:
            m.set_fill(color, opacity)
        return self

    def update(self, dt: float) -> None:
        super().update(dt)
        for m in self.submobjects:
            m.update(dt)
