"""Calculus Video Scenes inspired by Essence of Calculus."""

from __future__ import annotations
import numpy as np
from math_video_engine.scenes.base import Scene
from math_video_engine.objects.coordinate_plane import NumberPlane
from math_video_engine.objects.function_graph import FunctionGraph, RiemannRectangles, TangentLine
from math_video_engine.objects.geometry import Dot, Line
from math_video_engine.objects.text import Text, MathLabel
from math_video_engine.animations.base import FadeIn, FadeOut, Wait
from math_video_engine.animations.transform import Create, Transform
from math_video_engine.colors import BLUE, YELLOW, GREEN, RED, WHITE, GOLD, PURPLE


class DerivativeTangentScene(Scene):
    """Visualizes secant slope converging to instantaneous tangent: df/dx = lim(dx->0) dy/dx."""

    def construct(self) -> None:
        title = Text("Essence of Calculus: The Derivative Paradox", point=(0.0, 3.4), font_size=24, color=WHITE)
        formula = MathLabel("df/dx = lim(dx -> 0) [f(x + dx) - f(x)] / dx", point=(0.0, 2.8), color=YELLOW)

        plane = NumberPlane()
        self.add(plane, title, formula)

        # Function f(x) = 0.35 * x^2
        f = lambda x: 0.35 * x * x
        graph = FunctionGraph(f, x_range=(-4.0, 4.0, 150), color=BLUE, stroke_width=3.5)
        self.add(graph)

        x0 = 1.5
        y0 = f(x0)
        target_dot = Dot(point=(x0, y0), radius=0.1, color=YELLOW)

        # Secant line for large dx = 1.5
        dx_init = 1.5
        x1_init = x0 + dx_init
        y1_init = f(x1_init)
        moving_dot = Dot(point=(x1_init, y1_init), radius=0.1, color=RED)
        secant_line = Line(
            start=(x0 - 1.5, y0 - 1.5 * ((y1_init - y0) / dx_init)),
            end=(x1_init + 1.0, y1_init + 1.0 * ((y1_init - y0) / dx_init)),
            color=RED,
            stroke_width=2.5
        )

        # Instantaneous tangent line
        tangent = TangentLine(f, x_0=x0, length=4.5, color=GREEN, stroke_width=3.5)

        self.play(Create(graph), run_time=1.2)
        self.play(FadeIn(target_dot), FadeIn(moving_dot), Create(secant_line), run_time=1.0)
        self.wait(0.5)

        # Converge dx -> 0
        self.play(
            Transform(moving_dot, target_dot, run_time=2.0),
            Transform(secant_line, tangent, run_time=2.0),
        )
        tangent_label = MathLabel("Tangent Line (Slope = 1.05)", point=(2.5, 1.2), color=GREEN)
        self.play(FadeIn(tangent_label), run_time=0.8)
        self.wait(1.0)


class RiemannIntegralScene(Scene):
    """Visualizes integration as area under a curve approximated by Riemann sums."""

    def construct(self) -> None:
        title = Text("Integration: Riemann Sums Approximating Area", point=(0.0, 3.4), font_size=24, color=WHITE)
        integral_label = MathLabel("Area = Integral(0 to 3) [0.25*x^2 + 0.5] dx", point=(0.0, 2.8), color=GOLD)

        plane = NumberPlane()
        self.add(plane, title, integral_label)

        f = lambda x: 0.25 * x * x + 0.5
        graph = FunctionGraph(f, x_range=(-1.0, 4.0, 150), color=BLUE, stroke_width=3.5)
        self.add(graph)

        # Step 1: 4 coarse rectangles
        rects_4 = RiemannRectangles(f, x_range=(0.0, 3.0), num_rectangles=4, stroke_color=YELLOW, fill_color=YELLOW, fill_opacity=0.35)
        label_4 = Text("N = 4 Rectangles", point=(1.5, -0.6), color=YELLOW, font_size=18)

        # Step 2: 12 refined rectangles
        rects_12 = RiemannRectangles(f, x_range=(0.0, 3.0), num_rectangles=12, stroke_color=GREEN, fill_color=GREEN, fill_opacity=0.45)
        label_12 = Text("N = 12 Rectangles", point=(1.5, -0.6), color=GREEN, font_size=18)

        # Step 3: 30 fine rectangles
        rects_30 = RiemannRectangles(f, x_range=(0.0, 3.0), num_rectangles=30, stroke_color=BLUE, fill_color=BLUE, fill_opacity=0.55)
        label_30 = Text("N = 30 Rectangles -> Smooth Definite Integral", point=(1.5, -0.6), color=BLUE, font_size=18)

        self.play(Create(rects_4), FadeIn(label_4), run_time=1.5)
        self.wait(0.8)

        self.play(
            Transform(rects_4, rects_12, run_time=1.5),
            Transform(label_4, label_12, run_time=1.5),
        )
        self.wait(0.8)

        self.play(
            Transform(rects_4, rects_30, run_time=1.5),
            Transform(label_4, label_30, run_time=1.5),
        )
        self.wait(1.0)


class TaylorSeriesScene(Scene):
    """Visualizes Taylor polynomials approximating sin(x) to higher orders."""

    def construct(self) -> None:
        title = Text("Taylor Series: Polynomial Approximations of sin(x)", point=(0.0, 3.4), font_size=24, color=WHITE)

        plane = NumberPlane()
        self.add(plane, title)

        # Base curve sin(x)
        f_sin = lambda x: np.sin(x)
        graph_sin = FunctionGraph(f_sin, x_range=(-5.0, 5.0, 200), color=WHITE, stroke_width=3.5)
        sin_label = MathLabel("f(x) = sin(x)", point=(4.2, 1.2), color=WHITE)
        self.add(graph_sin, sin_label)

        # P_1(x) = x
        p1 = lambda x: x
        graph_p1 = FunctionGraph(p1, x_range=(-2.5, 2.5, 100), color=RED, stroke_width=3.0)
        label_p1 = MathLabel("P1(x) = x", point=(0.0, 2.7), color=RED)

        # P_3(x) = x - x^3/6
        p3 = lambda x: x - (x**3) / 6.0
        graph_p3 = FunctionGraph(p3, x_range=(-3.2, 3.2, 120), color=YELLOW, stroke_width=3.0)
        label_p3 = MathLabel("P3(x) = x - x^3/6", point=(0.0, 2.7), color=YELLOW)

        # P_5(x) = x - x^3/6 + x^5/120
        p5 = lambda x: x - (x**3) / 6.0 + (x**5) / 120.0
        graph_p5 = FunctionGraph(p5, x_range=(-4.0, 4.0, 150), color=GREEN, stroke_width=3.0)
        label_p5 = MathLabel("P5(x) = x - x^3/6 + x^5/120", point=(0.0, 2.7), color=GREEN)

        self.play(Create(graph_p1), FadeIn(label_p1), run_time=1.2)
        self.wait(0.8)

        self.play(
            Transform(graph_p1, graph_p3, run_time=1.5),
            Transform(label_p1, label_p3, run_time=1.5),
        )
        self.wait(0.8)

        self.play(
            Transform(graph_p1, graph_p5, run_time=1.5),
            Transform(label_p1, label_p5, run_time=1.5),
        )
        self.wait(1.0)
