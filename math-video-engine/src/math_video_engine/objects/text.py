"""Text and mathematical notation objects."""

from __future__ import annotations
import numpy as np
from typing import Sequence, Optional
from math_video_engine.objects.base import MObject
from math_video_engine.colors import WHITE


class Text(MObject):
    """Text label placed at world coordinates."""

    def __init__(
        self,
        text: str,
        point: Sequence[float] = (0.0, 0.0),
        font_size: int = 24,
        color: str = WHITE,
        alignment: str = "center",  # "left", "center", "right"
        **kwargs
    ):
        super().__init__(stroke_color=color, fill_color=color, fill_opacity=1.0, **kwargs)
        self.text = text
        self.point = np.array(point[:2], dtype=float)
        self.font_size = font_size
        self.alignment = alignment

    def get_center(self) -> np.ndarray:
        return self.point.copy()

    def shift(self, vector: Sequence[float]) -> Text:
        self.point += np.array(vector[:2], dtype=float)
        return self

    def set_text(self, new_text: str) -> Text:
        self.text = new_text
        return self


class MathLabel(Text):
    """Specialized mathematical formula label."""

    def __init__(
        self,
        formula: str,
        point: Sequence[float] = (0.0, 0.0),
        font_size: int = 26,
        color: str = WHITE,
        **kwargs
    ):
        super().__init__(text=formula, point=point, font_size=font_size, color=color, **kwargs)
