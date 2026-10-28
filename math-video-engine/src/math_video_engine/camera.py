"""Camera and coordinate transformations between world and pixel spaces."""

from __future__ import annotations
import numpy as np
from typing import Tuple, Union, Sequence


class Camera:
    """Manages 2D orthographic projection from world coordinates to pixel coordinates."""

    def __init__(
        self,
        pixel_width: int = 1280,
        pixel_height: int = 720,
        frame_width: float = 14.2222,
        frame_height: float = 8.0,
        frame_center: Sequence[float] = (0.0, 0.0),
    ):
        self.pixel_width = pixel_width
        self.pixel_height = pixel_height
        self.frame_width = float(frame_width)
        self.frame_height = float(frame_height)
        self.frame_center = np.array(frame_center, dtype=float)

    @property
    def pixels_per_unit_x(self) -> float:
        return self.pixel_width / self.frame_width

    @property
    def pixels_per_unit_y(self) -> float:
        return self.pixel_height / self.frame_height

    def world_to_pixel(self, point: Union[Sequence[float], np.ndarray]) -> Tuple[int, int]:
        """Convert a 2D world coordinate (x, y) to integer pixel coordinates (px, py)."""
        pt = np.asarray(point, dtype=float)
        rel_x = pt[0] - self.frame_center[0]
        rel_y = pt[1] - self.frame_center[1]

        px = int(round(self.pixel_width / 2.0 + rel_x * self.pixels_per_unit_x))
        # Note inverted y-axis in raster screen coordinates
        py = int(round(self.pixel_height / 2.0 - rel_y * self.pixels_per_unit_y))
        return px, py

    def pixel_to_world(self, pixel: Tuple[int, int]) -> np.ndarray:
        """Convert screen pixel coordinates (px, py) back to world coordinates (x, y)."""
        px, py = pixel
        rel_x = (px - self.pixel_width / 2.0) / self.pixels_per_unit_x
        rel_y = -(py - self.pixel_height / 2.0) / self.pixels_per_unit_y
        return np.array([rel_x + self.frame_center[0], rel_y + self.frame_center[1]], dtype=float)

    def world_distance_to_pixels(self, dist: float) -> float:
        """Convert scalar distance from world units to pixels (using average scale)."""
        return dist * ((self.pixels_per_unit_x + self.pixels_per_unit_y) / 2.0)

    def set_frame_center(self, center: Sequence[float]) -> None:
        """Pan camera frame to center coordinates."""
        self.frame_center = np.array(center, dtype=float)

    def zoom(self, factor: float) -> None:
        """Zoom in (>1.0) or zoom out (<1.0) by scaling the visible frame boundaries."""
        if factor <= 0.0:
            raise ValueError("Zoom factor must be strictly positive.")
        self.frame_width /= factor
        self.frame_height /= factor
