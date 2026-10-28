"""2D Canvas Renderer using Pillow and NumPy."""

from __future__ import annotations
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import List, Sequence, Tuple, Optional

from math_video_engine.camera import Camera
from math_video_engine.config import RenderConfig
from math_video_engine.colors import hex_to_rgba, hex_to_rgb
from math_video_engine.objects.base import MObject, VGroup
from math_video_engine.objects.geometry import (
    Dot, Line, Arrow, Polygon, Rectangle, Square, Circle, Arc
)
from math_video_engine.objects.vector import Vector
from math_video_engine.objects.function_graph import ParametricCurve
from math_video_engine.objects.text import Text


class Renderer:
    """Renders scenes of MObjects to raster images using Camera projections."""

    def __init__(self, camera: Camera, config: RenderConfig):
        self.camera = camera
        self.config = config

    def flatten_mobjects(self, mobjects: Sequence[MObject]) -> List[MObject]:
        """Recursively flatten VGroup hierarchies and sort by z_index."""
        flat: List[MObject] = []
        for m in mobjects:
            if not m.visible:
                continue
            if isinstance(m, VGroup):
                flat.extend(self.flatten_mobjects(m.submobjects))
            else:
                flat.append(m)
        flat.sort(key=lambda obj: obj.z_index)
        return flat

    def render_frame(self, mobjects: Sequence[MObject]) -> Image.Image:
        """Render a single frame containing mobjects into a PIL RGBA Image."""
        # Create base canvas with background color
        bg_rgb = hex_to_rgb(self.config.background_color)
        canvas = Image.new("RGBA", (self.config.width, self.config.height), (*bg_rgb, 255))
        overlay = Image.new("RGBA", (self.config.width, self.config.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        flat_objects = self.flatten_mobjects(mobjects)

        for m in flat_objects:
            self._draw_mobject(m, draw)

        # Alpha composite transparent overlay over base canvas
        return Image.alpha_composite(canvas, overlay)

    def _draw_mobject(self, m: MObject, draw: ImageDraw.ImageDraw) -> None:
        if isinstance(m, Arrow) or isinstance(m, Vector):
            self._draw_arrow(m, draw)
        elif isinstance(m, Line):
            self._draw_line(m, draw)
        elif isinstance(m, Polygon):
            self._draw_polygon(m, draw)
        elif isinstance(m, Dot):
            self._draw_dot(m, draw)
        elif isinstance(m, Circle):
            self._draw_circle(m, draw)
        elif isinstance(m, Arc):
            self._draw_arc(m, draw)
        elif isinstance(m, ParametricCurve):
            self._draw_curve(m, draw)
        elif isinstance(m, Text):
            self._draw_text(m, draw)

    def _draw_line(self, line: Line, draw: ImageDraw.ImageDraw) -> None:
        p1 = self.camera.world_to_pixel(line.start)
        p2 = self.camera.world_to_pixel(line.end)
        rgba = hex_to_rgba(line.stroke_color, line.stroke_opacity)
        width = max(1, int(round(line.stroke_width)))
        draw.line([p1, p2], fill=rgba, width=width)

    def _draw_arrow(self, arrow: Arrow, draw: ImageDraw.ImageDraw) -> None:
        # Shaft
        self._draw_line(arrow, draw)
        # Tip
        tip, left, right = arrow.get_tip_points()
        p_tip = self.camera.world_to_pixel(tip)
        p_left = self.camera.world_to_pixel(left)
        p_right = self.camera.world_to_pixel(right)
        rgba = hex_to_rgba(arrow.stroke_color, arrow.stroke_opacity)
        draw.polygon([p_tip, p_left, p_right], fill=rgba, outline=rgba)

    def _draw_polygon(self, poly: Polygon, draw: ImageDraw.ImageDraw) -> None:
        if len(poly.vertices) < 3:
            return
        px_verts = [self.camera.world_to_pixel(v) for v in poly.vertices]

        # Fill
        if poly.fill_color is not None and poly.fill_opacity > 0:
            fill_rgba = hex_to_rgba(poly.fill_color, poly.fill_opacity)
            draw.polygon(px_verts, fill=fill_rgba)

        # Stroke outline
        if poly.stroke_width > 0 and poly.stroke_opacity > 0:
            stroke_rgba = hex_to_rgba(poly.stroke_color, poly.stroke_opacity)
            width = max(1, int(round(poly.stroke_width)))
            draw.polygon(px_verts, outline=stroke_rgba, width=width)

    def _draw_dot(self, dot: Dot, draw: ImageDraw.ImageDraw) -> None:
        px, py = self.camera.world_to_pixel(dot.point)
        r_px = max(1.0, self.camera.world_distance_to_pixels(dot.radius))
        bbox = [px - r_px, py - r_px, px + r_px, py + r_px]
        fill_rgba = hex_to_rgba(dot.fill_color or dot.stroke_color, dot.fill_opacity)
        draw.ellipse(bbox, fill=fill_rgba)

    def _draw_circle(self, circle: Circle, draw: ImageDraw.ImageDraw) -> None:
        px, py = self.camera.world_to_pixel(circle.center)
        r_px = max(1.0, self.camera.world_distance_to_pixels(circle.radius))
        bbox = [px - r_px, py - r_px, px + r_px, py + r_px]

        # Fill
        if circle.fill_color is not None and circle.fill_opacity > 0:
            fill_rgba = hex_to_rgba(circle.fill_color, circle.fill_opacity)
            draw.ellipse(bbox, fill=fill_rgba)

        # Stroke
        if circle.stroke_width > 0 and circle.stroke_opacity > 0:
            stroke_rgba = hex_to_rgba(circle.stroke_color, circle.stroke_opacity)
            width = max(1, int(round(circle.stroke_width)))
            draw.ellipse(bbox, outline=stroke_rgba, width=width)

    def _draw_arc(self, arc: Arc, draw: ImageDraw.ImageDraw) -> None:
        pts = arc.get_points()
        if len(pts) < 2:
            return
        px_pts = [self.camera.world_to_pixel(p) for p in pts]
        rgba = hex_to_rgba(arc.stroke_color, arc.stroke_opacity)
        width = max(1, int(round(arc.stroke_width)))
        draw.line(px_pts, fill=rgba, width=width)

    def _draw_curve(self, curve: ParametricCurve, draw: ImageDraw.ImageDraw) -> None:
        if len(curve.points) < 2:
            return
        px_pts = [self.camera.world_to_pixel(p) for p in curve.points]
        rgba = hex_to_rgba(curve.stroke_color, curve.stroke_opacity)
        width = max(1, int(round(curve.stroke_width)))
        draw.line(px_pts, fill=rgba, width=width)

    def _draw_text(self, text: Text, draw: ImageDraw.ImageDraw) -> None:
        px, py = self.camera.world_to_pixel(text.point)
        font = ImageFont.load_default()
        rgba = hex_to_rgba(text.stroke_color, text.stroke_opacity)

        # Approximate bounding box for alignment
        bbox = draw.textbbox((0, 0), text.text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        if text.alignment == "center":
            draw_x = px - text_w // 2
        elif text.alignment == "right":
            draw_x = px - text_w
        else:
            draw_x = px
        draw_y = py - text_h // 2

        draw.text((draw_x, draw_y), text.text, fill=rgba, font=font)
