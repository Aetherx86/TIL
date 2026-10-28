"""Fourier Transform and Harmonic Analysis Scenes."""

from __future__ import annotations
import math
import numpy as np
from math_video_engine.scenes.base import Scene
from math_video_engine.objects.coordinate_plane import NumberPlane
from math_video_engine.objects.geometry import Circle, Line, Dot
from math_video_engine.objects.function_graph import FunctionGraph
from math_video_engine.objects.text import Text, MathLabel
from math_video_engine.animations.base import FadeIn, FadeOut, Wait
from math_video_engine.animations.transform import Create, Transform
from math_video_engine.colors import BLUE, YELLOW, GREEN, RED, WHITE, PURPLE, GOLD


class FourierEpicyclesScene(Scene):
    """Visualizes rotating complex vectors (epicycles) tracing periodic trajectories."""

    def construct(self) -> None:
        title = Text("Fourier Epicycles: Rotating Vectors Tracing Curves", point=(0.0, 3.4), font_size=24, color=WHITE)
        formula = MathLabel("z(t) = Sum c_k * exp(i * k * omega * t)", point=(0.0, 2.8), color=GOLD)

        plane = NumberPlane()
        self.add(plane, title, formula)

        # Epicycle parameters: (radius, frequency)
        c1 = Circle(radius=1.8, center=(0.0, 0.0), color="#304562", stroke_width=1.5)
        v1 = Line(start=(0.0, 0.0), end=(1.8, 0.0), color=YELLOW, stroke_width=3.0)

        c2 = Circle(radius=0.7, center=(1.8, 0.0), color="#304562", stroke_width=1.5)
        v2 = Line(start=(1.8, 0.0), end=(2.5, 0.0), color=GREEN, stroke_width=3.0)

        c3 = Circle(radius=0.3, center=(2.5, 0.0), color="#304562", stroke_width=1.5)
        v3 = Line(start=(2.5, 0.0), end=(2.8, 0.0), color=RED, stroke_width=3.0)

        tip_dot = Dot(point=(2.8, 0.0), radius=0.08, color=WHITE)

        self.add(c1, v1, c2, v2, c3, v3, tip_dot)

        # Dynamic rotational updater
        state = {"time": 0.0}

        def update_epicycles(m, dt):
            state["time"] += dt
            t = state["time"]

            # Vector 1
            theta1 = 1.0 * t
            p1 = np.array([1.8 * math.cos(theta1), 1.8 * math.sin(theta1)])
            v1.start = np.zeros(2)
            v1.end = p1

            # Vector 2 (rotates relative to p1)
            theta2 = -2.5 * t
            p2 = p1 + np.array([0.7 * math.cos(theta2), 0.7 * math.sin(theta2)])
            c2.center = p1
            v2.start = p1
            v2.end = p2

            # Vector 3 (rotates relative to p2)
            theta3 = 4.0 * t
            p3 = p2 + np.array([0.3 * math.cos(theta3), 0.3 * math.sin(theta3)])
            c3.center = p2
            v3.start = p2
            v3.end = p3

            tip_dot.point = p3

        v1.add_updater(update_epicycles)
        self.wait(3.5)


class FourierWaveDecompositionScene(Scene):
    """Visualizes decomposing a square wave into its harmonic Fourier series."""

    def construct(self) -> None:
        title = Text("Harmonic Wave Decomposition", point=(0.0, 3.4), font_size=24, color=WHITE)
        formula = MathLabel("Square(t) ~ 4/pi * [sin(t) + 1/3*sin(3t) + 1/5*sin(5t)]", point=(0.0, 2.8), color=YELLOW)

        plane = NumberPlane()
        self.add(plane, title, formula)

        # Component 1: Fundamental sin(x)
        w1 = lambda x: (4.0 / np.pi) * np.sin(x)
        graph1 = FunctionGraph(w1, x_range=(-5.0, 5.0, 180), color=BLUE, stroke_width=3.0)
        label1 = MathLabel("1st Harmonic: sin(t)", point=(-2.8, 1.8), color=BLUE)

        # Component 1 + 2: sin(x) + (1/3)*sin(3x)
        w2 = lambda x: (4.0 / np.pi) * (np.sin(x) + (1.0 / 3.0) * np.sin(3.0 * x))
        graph2 = FunctionGraph(w2, x_range=(-5.0, 5.0, 220), color=GREEN, stroke_width=3.0)
        label2 = MathLabel("1st + 3rd Harmonics", point=(-2.8, 1.8), color=GREEN)

        # Component 1 + 2 + 3: sin(x) + (1/3)*sin(3x) + (1/5)*sin(5x)
        w3 = lambda x: (4.0 / np.pi) * (
            np.sin(x) + (1.0 / 3.0) * np.sin(3.0 * x) + (1.0 / 5.0) * np.sin(5.0 * x)
        )
        graph3 = FunctionGraph(w3, x_range=(-5.0, 5.0, 250), color=YELLOW, stroke_width=3.5)
        label3 = MathLabel("1st + 3rd + 5th Harmonics (Square Wave Approximant)", point=(-1.2, 1.8), color=YELLOW)

        self.play(Create(graph1), FadeIn(label1), run_time=1.2)
        self.wait(0.8)

        self.play(
            Transform(graph1, graph2, run_time=1.5),
            Transform(label1, label2, run_time=1.5),
        )
        self.wait(0.8)

        self.play(
            Transform(graph1, graph3, run_time=1.5),
            Transform(label1, label3, run_time=1.5),
        )
        self.wait(1.0)
