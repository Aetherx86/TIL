"""Vector representations for linear algebra scenes."""

from __future__ import annotations
import numpy as np
from typing import Sequence, Optional, Tuple
from math_video_engine.objects.geometry import Arrow
from math_video_engine.objects.base import VGroup
from math_video_engine.colors import YELLOW, GREEN, RED, BLUE


class Vector(Arrow):
    """A mathematical 2D vector represented as a directed arrow from origin to coordinates."""

    def __init__(
        self,
        coords: Sequence[float] = (1.0, 0.0),
        tail: Sequence[float] = (0.0, 0.0),
        color: str = YELLOW,
        stroke_width: float = 3.5,
        tip_length: float = 0.3,
        **kwargs
    ):
        tail_pt = np.array(tail[:2], dtype=float)
        tip_pt = tail_pt + np.array(coords[:2], dtype=float)
        super().__init__(start=tail_pt, end=tip_pt, color=color, stroke_width=stroke_width, tip_length=tip_length, **kwargs)
        self.coords = np.array(coords[:2], dtype=float)

    def apply_matrix(self, matrix: np.ndarray) -> Vector:
        """Transform vector by a 2x2 matrix."""
        mat = np.asarray(matrix, dtype=float)
        self.start = self.start @ mat.T
        self.end = self.end @ mat.T
        self.coords = self.end - self.start
        return self


class BasisVectors(VGroup):
    """The canonical i-hat and j-hat unit basis vectors of R^2."""

    def __init__(
        self,
        i_color: str = GREEN,
        j_color: str = RED,
        stroke_width: float = 4.0,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.i_hat = Vector(coords=(1.0, 0.0), color=i_color, stroke_width=stroke_width)
        self.j_hat = Vector(coords=(0.0, 1.0), color=j_color, stroke_width=stroke_width)
        self.add(self.i_hat, self.j_hat)

    def apply_matrix(self, matrix: np.ndarray) -> BasisVectors:
        self.i_hat.apply_matrix(matrix)
        self.j_hat.apply_matrix(matrix)
        return self
