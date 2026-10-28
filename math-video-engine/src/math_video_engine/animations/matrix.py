"""Linear transformation and matrix animations."""

from __future__ import annotations
import numpy as np
from typing import Sequence
from math_video_engine.animations.base import Animation
from math_video_engine.objects.base import MObject
from math_video_engine.objects.coordinate_plane import NumberPlane
from math_video_engine.objects.vector import Vector, BasisVectors
from math_video_engine.objects.geometry import Polygon
from math_video_engine.easing import smooth, RateFunc


class ApplyMatrix(Animation):
    """Smoothly apply a 2x2 linear transformation matrix to a mobject or grid."""

    def __init__(
        self,
        mobject: MObject,
        matrix: Sequence[Sequence[float]],
        run_time: float = 2.0,
        rate_func: RateFunc = smooth,
    ):
        super().__init__(mobject=mobject, run_time=run_time, rate_func=rate_func)
        self.target_matrix = np.array(matrix, dtype=float)
        if self.target_matrix.shape != (2, 2):
            raise ValueError(f"Matrix must have shape (2, 2), got {self.target_matrix.shape}")
        self.identity = np.eye(2, dtype=float)

    def begin(self) -> None:
        super().begin()
        self.start_snapshot = self.mobject.copy()

    def interpolate(self, alpha: float) -> None:
        # Interpolated matrix: (1 - alpha)*I + alpha*M
        current_mat = (1.0 - alpha) * self.identity + alpha * self.target_matrix
        self._apply_interpolated(current_mat)

    def _apply_interpolated(self, mat: np.ndarray) -> None:
        if isinstance(self.mobject, NumberPlane) and isinstance(self.start_snapshot, NumberPlane):
            # Transform grid lines
            for orig_line, curr_line in zip(self.start_snapshot.grid_lines, self.mobject.grid_lines):
                curr_line.start = orig_line.start @ mat.T
                curr_line.end = orig_line.end @ mat.T
            # Transform main axes
            self.mobject.axes.x_axis.start = self.start_snapshot.axes.x_axis.start @ mat.T
            self.mobject.axes.x_axis.end = self.start_snapshot.axes.x_axis.end @ mat.T
            self.mobject.axes.y_axis.start = self.start_snapshot.axes.y_axis.start @ mat.T
            self.mobject.axes.y_axis.end = self.start_snapshot.axes.y_axis.end @ mat.T
        elif isinstance(self.mobject, BasisVectors) and isinstance(self.start_snapshot, BasisVectors):
            self.mobject.i_hat.start = self.start_snapshot.i_hat.start @ mat.T
            self.mobject.i_hat.end = self.start_snapshot.i_hat.end @ mat.T
            self.mobject.j_hat.start = self.start_snapshot.j_hat.start @ mat.T
            self.mobject.j_hat.end = self.start_snapshot.j_hat.end @ mat.T
        elif isinstance(self.mobject, Vector) and isinstance(self.start_snapshot, Vector):
            self.mobject.start = self.start_snapshot.start @ mat.T
            self.mobject.end = self.start_snapshot.end @ mat.T
            self.mobject.coords = self.mobject.end - self.mobject.start
        elif isinstance(self.mobject, Polygon) and isinstance(self.start_snapshot, Polygon):
            self.mobject.vertices = self.start_snapshot.vertices @ mat.T
