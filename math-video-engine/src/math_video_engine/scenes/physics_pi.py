"""Physics and Pure Mathematics Scenes (Pi Collisions and Basel Problem)."""

from __future__ import annotations
import numpy as np
from math_video_engine.scenes.base import Scene
from math_video_engine.objects.coordinate_plane import NumberPlane
from math_video_engine.objects.geometry import Rectangle, Square, Line, Circle, Dot
from math_video_engine.objects.text import Text, MathLabel
from math_video_engine.animations.base import FadeIn, FadeOut, Wait
from math_video_engine.animations.transform import Create
from math_video_engine.animations.movement import Shift
from math_video_engine.colors import BLUE, YELLOW, GREEN, RED, WHITE, GOLD


class PiCollidingBlocksScene(Scene):
    """Visualizes Galperin's billiard ball method calculating digits of Pi via elastic collisions."""

    def construct(self) -> None:
        title = Text("Computing Pi with Colliding Blocks (Galperin's Method)", point=(0.0, 3.4), font_size=24, color=WHITE)
        subtitle = MathLabel("Mass Ratio M/m = 100^d  ==>  Collisions = floor(pi * 10^d)", point=(0.0, 2.8), color=GOLD)
        self.add(title, subtitle)

        # Floor and Left Wall
        floor = Line(start=(-6.0, -1.5), end=(6.0, -1.5), color=WHITE, stroke_width=3.5)
        wall = Line(start=(-5.0, -1.5), end=(-5.0, 2.0), color=WHITE, stroke_width=4.5)
        self.add(floor, wall)

        # Small block (m = 1)
        block_small = Square(side_length=0.8, center=(-2.0, -1.1), stroke_color=YELLOW, fill_color=YELLOW, fill_opacity=0.4)
        label_small = Text("m = 1", point=(-2.0, -0.4), color=YELLOW, font_size=16)

        # Large block (M = 16 for visual clarity)
        block_big = Rectangle(width=1.6, height=1.6, center=(2.5, -0.7), stroke_color=RED, fill_color=RED, fill_opacity=0.4)
        label_big = Text("M = 16", point=(2.5, 0.4), color=RED, font_size=16)

        collision_counter = Text("Collisions: 0", point=(0.0, 1.8), color=GREEN, font_size=22)

        self.add(block_small, label_small, block_big, label_big, collision_counter)
        self.wait(0.6)

        # Simulate collision sequence: Big block moves left, strikes small block
        # 1. Big block moves in
        self.play(
            Shift(block_big, vector=(-3.2, 0.0)),
            Shift(label_big, vector=(-3.2, 0.0)),
            run_time=1.0
        )
        # Collision 1: Big strikes Small
        collision_counter.set_text("Collisions: 1")
        self.play(
            Shift(block_small, vector=(-2.2, 0.0)),
            Shift(label_small, vector=(-2.2, 0.0)),
            run_time=0.6
        )
        # Collision 2: Small hits wall and rebounds
        collision_counter.set_text("Collisions: 2")
        self.play(
            Shift(block_small, vector=(1.8, 0.0)),
            Shift(label_small, vector=(1.8, 0.0)),
            run_time=0.6
        )
        # Collision 3: Small strikes Big again
        collision_counter.set_text("Collisions: 3 (Ratio Pi Approximant)")
        self.wait(1.0)


class BaselProblemScene(Scene):
    """Visualizes Euler's solution to the Basel problem: Sum 1/n^2 = pi^2 / 6."""

    def construct(self) -> None:
        title = Text("The Basel Problem: Inverse Square Light and Pi", point=(0.0, 3.4), font_size=24, color=WHITE)
        formula = MathLabel("Sum_(n=1..inf) 1/n^2 = pi^2 / 6 ~ 1.64493", point=(0.0, 2.8), color=GOLD)

        plane = NumberPlane()
        self.add(plane, title, formula)

        # Origin lighthouse
        lighthouse = Dot(point=(0.0, 0.0), radius=0.15, color=YELLOW)
        self.add(lighthouse)

        # Concentric distance circles
        radii = [1.0, 2.0, 3.0, 4.0]
        colors = [YELLOW, GREEN, BLUE, RED]
        for r, col in zip(radii, colors):
            circle = Circle(radius=r, center=(0.0, 0.0), color=col, stroke_width=2.0)
            dot_pt = Dot(point=(r, 0.0), radius=0.08, color=col)
            label = MathLabel(f"1/{int(r)}^2 = {1.0/(r*r):.2f}", point=(r + 0.6, 0.3), color=col, font_size=16)
            self.play(Create(circle), FadeIn(dot_pt), FadeIn(label), run_time=0.7)

        conclusion = Text("Summing infinite lighthouse brightness yields exactly pi^2 / 6", point=(0.0, -3.2), font_size=20, color=WHITE)
        self.play(FadeIn(conclusion), run_time=1.0)
        self.wait(1.0)
