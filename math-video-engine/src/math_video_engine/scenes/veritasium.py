"""Veritasium Mathematical & Scientific Paradox Visualizations."""

from __future__ import annotations
import math
import numpy as np
from typing import List, Tuple

from math_video_engine.scenes.base import Scene
from math_video_engine.objects.coordinate_plane import NumberPlane
from math_video_engine.objects.geometry import Dot, Line, Rectangle, Circle, Arrow, Arc
from math_video_engine.objects.function_graph import FunctionGraph, ParametricCurve
from math_video_engine.objects.text import Text, MathLabel
from math_video_engine.animations.base import FadeIn, FadeOut, Wait
from math_video_engine.animations.transform import Create, Transform
from math_video_engine.animations.movement import Shift
from math_video_engine.colors import (
    BLUE, YELLOW, GREEN, RED, GOLD, WHITE, PURPLE, TEAL, GRAY_C, GRAY_D
)


class CollatzConjectureScene(Scene):
    """Visualizes Veritasium's 'The Simplest Math Problem No One Can Solve' (3x + 1 Collatz Conjecture)."""

    def construct(self) -> None:
        title = Text("The Collatz Conjecture (Veritasium: The 3x+1 Problem)", point=(0.0, 3.4), font_size=24, color=WHITE)
        rule = MathLabel("n -> n / 2 (if even)  |  n -> 3n + 1 (if odd)", point=(0.0, 2.8), color=GOLD)
        status = Text("Every tested number eventually collapses into the 4 -> 2 -> 1 loop", point=(0.0, 2.3), font_size=18, color=YELLOW)

        plane = NumberPlane(
            x_range=(-6.0, 6.0, 1.0),
            y_range=(-3.5, 3.5, 1.0)
        )
        self.add(plane, title, rule, status)

        # Hailstone trajectory for start number 27 (famous 111-step ascent peaking at 9232)
        # We visualize normalized steps for start = 7: [7, 22, 11, 34, 17, 52, 26, 13, 40, 20, 10, 5, 16, 8, 4, 2, 1]
        trajectory = [7, 22, 11, 34, 17, 52, 26, 13, 40, 20, 10, 5, 16, 8, 4, 2, 1]
        max_val = 52.0
        n_steps = len(trajectory)

        start_lbl = MathLabel(f"Seed n = {trajectory[0]} (Reaches peak {int(max_val)}, collapses to 1 in {n_steps - 1} steps)", point=(0.0, -2.8), color=GREEN, font_size=18)
        self.add(start_lbl)

        # Plot discrete trajectory points in world coordinates
        coords = []
        for i, val in enumerate(trajectory):
            wx = -5.0 + (i / (n_steps - 1)) * 10.0
            wy = -1.5 + (val / max_val) * 3.2
            coords.append((wx, wy))

        dots = []
        lines = []
        for i in range(len(coords)):
            d = Dot(point=coords[i], radius=0.08, color=YELLOW if i < len(coords) - 3 else RED)
            dots.append(d)
            if i > 0:
                line = Line(start=coords[i - 1], end=coords[i], color=BLUE if coords[i][1] < coords[i-1][1] else GOLD, stroke_width=2.5)
                lines.append(line)

        self.wait(0.5)

        for i in range(len(lines)):
            self.play(Create(lines[i]), FadeIn(dots[i + 1]), run_time=0.15)

        loop_box = Rectangle(width=3.6, height=1.2, center=(3.8, -1.0), stroke_color=RED, fill_color="#241018", fill_opacity=0.8)
        loop_lbl = Text("4 -> 2 -> 1 Loop", point=(3.8, -1.0), font_size=18, color=RED)
        self.play(Create(loop_box), FadeIn(loop_lbl), run_time=0.8)
        self.wait(1.0)


class LogisticMapChaosScene(Scene):
    """Visualizes Veritasium's 'This Equation Will Change How You See The World' (Logistic Map & Chaos)."""

    def construct(self) -> None:
        title = Text("The Logistic Map and Chaos (Veritasium)", point=(0.0, 3.4), font_size=24, color=WHITE)
        formula = MathLabel("x_(n+1) = r * x_n * (1 - x_n)   [Period Doubling -> Chaos]", point=(0.0, 2.8), color=GOLD)
        feigen = Text("Feigenbaum Constant delta ~ 4.6692016... (Universal scaling ratio)", point=(0.0, 2.3), font_size=17, color=YELLOW)

        plane = NumberPlane(
            x_range=(-6.0, 6.0, 1.0),
            y_range=(-3.5, 3.5, 1.0)
        )
        self.add(plane, title, formula, feigen)

        # Axes labels: r in [2.4, 4.0] -> world x in [-5.0, 5.0]
        # x_inf in [0, 1] -> world y in [-2.0, 1.5]
        def r_to_x(r: float) -> float:
            return -5.0 + ((r - 2.4) / (4.0 - 2.4)) * 10.0

        def pop_to_y(x: float) -> float:
            return -2.0 + x * 3.5

        r_axis_lbl = Text("Growth Parameter r (2.4 -> 4.0)", point=(0.0, -2.4), font_size=16, color=WHITE)
        self.add(r_axis_lbl)

        # Regimes: Single stable point, period 2, period 4, chaos
        regime_1 = Line(start=(r_to_x(2.4), pop_to_y(0.6)), end=(r_to_x(3.0), pop_to_y(0.666)), color=BLUE, stroke_width=3.0)
        r1_lbl = Text("Stable Fixed Point (r < 3.0)", point=(-3.2, 0.8), font_size=15, color=BLUE)

        # Bifurcation at r=3.0 into 2 branches
        r_bif = np.linspace(3.0, 3.45, 30)
        pts_up = [(r_to_x(r), pop_to_y(0.5 + 0.5 * math.sqrt((r - 3.0) / 1.5))) for r in r_bif]
        pts_dn = [(r_to_x(r), pop_to_y(0.5 - 0.5 * math.sqrt((r - 3.0) / 1.5))) for r in r_bif]

        lines_up = [Line(start=pts_up[i], end=pts_up[i+1], color=GREEN, stroke_width=2.5) for i in range(len(pts_up)-1)]
        lines_dn = [Line(start=pts_dn[i], end=pts_dn[i+1], color=GREEN, stroke_width=2.5) for i in range(len(pts_dn)-1)]
        r2_lbl = Text("Period 2 Cycle", point=(-0.6, 1.2), font_size=15, color=GREEN)

        self.play(Create(regime_1), FadeIn(r1_lbl), run_time=1.0)
        self.wait(0.5)

        for lu, ld in zip(lines_up, lines_dn):
            self.add(lu, ld)
        self.play(FadeIn(r2_lbl), run_time=0.8)
        self.wait(0.5)

        # Chaos region r > 3.57
        chaos_zone = Rectangle(width=2.8, height=3.8, center=(3.6, -0.2), stroke_color=RED, fill_color="#241018", fill_opacity=0.35)
        chaos_lbl = Text("Deterministic Chaos (r > 3.5699)", point=(3.6, 1.4), font_size=16, color=RED)
        self.play(Create(chaos_zone), FadeIn(chaos_lbl), run_time=1.0)
        self.wait(1.0)


class HundredPrisonersRiddleScene(Scene):
    """Visualizes Veritasium's 'The Riddle That Seems Impossible Even If You Know The Answer'."""

    def construct(self) -> None:
        title = Text("The 100 Prisoners Problem (Veritasium)", point=(0.0, 3.4), font_size=24, color=WHITE)
        subtitle = MathLabel("Independent Random: (1/2)^100 ~ 8 * 10^-31  vs  Loop Strategy: 31.18%!", point=(0.0, 2.8), color=GOLD)
        strategy = Text("Strategy: Follow cycle permutations starting from your own prisoner number", point=(0.0, 2.3), font_size=17, color=YELLOW)

        self.add(title, subtitle, strategy)

        # Permutation cycle diagram
        cycle_nodes = [
            (0.0, 1.2, "Box 1 -> [7]"),
            (2.2, 0.4, "Box 7 -> [15]"),
            (1.8, -1.2, "Box 15 -> [42]"),
            (-1.8, -1.2, "Box 42 -> [88]"),
            (-2.2, 0.4, "Box 88 -> [1]"),
        ]

        dots = []
        labels = []
        for x, y, name in cycle_nodes:
            d = Dot(point=(x, y), radius=0.15, color=GREEN)
            lbl = Text(name, point=(x * 1.35, y * 1.25), font_size=15, color=WHITE)
            dots.append(d)
            labels.append(lbl)

        arrows = []
        for i in range(len(cycle_nodes)):
            p1 = cycle_nodes[i][:2]
            p2 = cycle_nodes[(i + 1) % len(cycle_nodes)][:2]
            arr = Arrow(start=p1, end=p2, color=YELLOW, stroke_width=3.0, tip_length=0.25)
            arrows.append(arr)

        self.wait(0.5)
        for i in range(len(dots)):
            self.play(FadeIn(dots[i]), FadeIn(labels[i]), Create(arrows[i]), run_time=0.4)

        result_box = Rectangle(width=10.0, height=1.1, center=(0.0, -2.6), stroke_color=GREEN, fill_color="#102418", fill_opacity=0.85)
        res_text = Text("Success condition: All cycle lengths <= 50. Probability = 1 - ln(2) = 31.18%", point=(0.0, -2.6), font_size=18, color=GREEN)
        self.play(Create(result_box), FadeIn(res_text), run_time=0.8)
        self.wait(1.0)


class OptimalStoppingScene(Scene):
    """Visualizes Veritasium's 'The 37% Rule for Optimal Decision Making' (The Secretary Problem)."""

    def construct(self) -> None:
        title = Text("The 37% Rule: Optimal Stopping Problem (Veritasium)", point=(0.0, 3.4), font_size=24, color=WHITE)
        subtitle = MathLabel("Reject first n / e ~ 36.8% candidates, then select first exceeding benchmark", point=(0.0, 2.8), color=GOLD)
        prob = Text("Theoretical Maximum Success Probability: 1 / e ~ 36.79%", point=(0.0, 2.3), font_size=17, color=YELLOW)

        plane = NumberPlane()
        self.add(plane, title, subtitle, prob)

        # Graph success probability P(r) as a function of rejection threshold r in [0, 1]
        # P(r) = -r * ln(r)
        def p_success(r: float) -> float:
            if r <= 0.0 or r >= 1.0:
                return 0.0
            return -r * math.log(r)

        # Map r in [0, 1] -> world x in [-4.0, 4.0]
        # Map P(r) in [0, 0.45] -> world y in [-1.8, 1.8]
        def r_to_world(r: float) -> Tuple[float, float]:
            wx = -4.0 + r * 8.0
            wy = -1.8 + (p_success(r) / 0.45) * 3.2
            return wx, wy

        rs = np.linspace(0.01, 0.99, 120)
        pts = [r_to_world(r) for r in rs]
        curve_lines = [Line(start=pts[i], end=pts[i+1], color=BLUE, stroke_width=3.5) for i in range(len(pts)-1)]

        for l in curve_lines:
            self.add(l)

        # Optimum at r = 1/e ~ 0.368, P = 1/e ~ 0.368
        opt_r = 1.0 / math.e
        opt_wx, opt_wy = r_to_world(opt_r)

        opt_dot = Dot(point=(opt_wx, opt_wy), radius=0.12, color=GREEN)
        opt_line = Line(start=(opt_wx, -1.8), end=(opt_wx, opt_wy), color=GREEN, stroke_width=2.0)
        opt_lbl = MathLabel(f"Optimum: r = 1/e (36.8%), P = 36.8%", point=(opt_wx + 0.8, opt_wy + 0.3), color=GREEN, font_size=18)

        reject_zone = Rectangle(width=(opt_wx - (-4.0)), height=3.6, center=((-4.0 + opt_wx)/2.0, -0.2), stroke_color=RED, fill_color="#241018", fill_opacity=0.3)
        reject_lbl = Text("Explore (Reject Phase: 36.8%)", point=((-4.0 + opt_wx)/2.0, -1.2), font_size=15, color=RED)

        select_zone = Rectangle(width=(4.0 - opt_wx), height=3.6, center=((opt_wx + 4.0)/2.0, -0.2), stroke_color=GREEN, fill_color="#102418", fill_opacity=0.3)
        select_lbl = Text("Exploit (Select Phase: 63.2%)", point=((opt_wx + 4.0)/2.0, -1.2), font_size=15, color=GREEN)

        self.play(FadeIn(reject_zone), FadeIn(reject_lbl), run_time=0.8)
        self.play(FadeIn(select_zone), FadeIn(select_lbl), run_time=0.8)
        self.play(Create(opt_line), FadeIn(opt_dot), FadeIn(opt_lbl), run_time=1.0)
        self.wait(1.0)


class DoubleSlitInterferenceScene(Scene):
    """Visualizes Veritasium's 'The Quantum Experiment That Broke Reality' (Wave Interference)."""

    def construct(self) -> None:
        title = Text("Wave-Particle Duality: Double Slit Interference (Veritasium)", point=(0.0, 3.4), font_size=24, color=WHITE)
        subtitle = MathLabel("Intensity I(theta) = I_0 * cos^2(pi*d*sin(theta)/lambda) * sinc^2(pi*a*sin(theta)/lambda)", point=(0.0, 2.8), color=GOLD)
        self.add(title, subtitle)

        # Left: Slit barrier
        barrier_top = Line(start=(-4.5, 2.2), end=(-4.5, 0.7), color=WHITE, stroke_width=5.0)
        barrier_mid = Line(start=(-4.5, 0.3), end=(-4.5, -0.3), color=WHITE, stroke_width=5.0)
        barrier_bot = Line(start=(-4.5, -0.7), end=(-4.5, -2.2), color=WHITE, stroke_width=5.0)
        slit1_lbl = Text("Slit 1", point=(-5.2, 0.5), font_size=14, color=YELLOW)
        slit2_lbl = Text("Slit 2", point=(-5.2, -0.5), font_size=14, color=YELLOW)

        # Right: Detection screen
        screen = Line(start=(4.0, 2.2), end=(4.0, -2.2), color=GRAY_C, stroke_width=4.0)
        screen_lbl = Text("Detector Screen", point=(4.8, 0.0), font_size=15, color=WHITE)

        self.add(barrier_top, barrier_mid, barrier_bot, slit1_lbl, slit2_lbl, screen, screen_lbl)

        # Draw interference fringes on screen as modulated brightness/bars
        # I(y) ~ cos^2(3*y) * exp(-0.4 * y^2)
        fringes = []
        for y in np.linspace(-2.0, 2.0, 25):
            intensity = (math.cos(3.5 * y) ** 2) * math.exp(-0.45 * y * y)
            bar_len = intensity * 1.8
            bar = Line(start=(4.0 - bar_len, y), end=(4.0, y), color=TEAL, stroke_width=3.0)
            fringes.append(bar)

        self.wait(0.5)

        # Animate concentric wavefronts expanding from each slit
        wave_arcs = []
        for r in [0.8, 1.6, 2.4, 3.2]:
            a1 = Arc(radius=r, start_angle=-math.pi/3, angle=2*math.pi/3, center=(-4.5, 0.5), color=BLUE, stroke_width=1.5)
            a2 = Arc(radius=r, start_angle=-math.pi/3, angle=2*math.pi/3, center=(-4.5, -0.5), color=BLUE, stroke_width=1.5)
            wave_arcs.extend([a1, a2])

        for w in wave_arcs:
            self.add(w)

        for f in fringes:
            self.play(Create(f), run_time=0.06)

        pattern_lbl = Text("Interference Fringe Pattern (Constructive / Destructive Waves)", point=(0.0, -2.6), font_size=18, color=TEAL)
        self.play(FadeIn(pattern_lbl), run_time=0.8)
        self.wait(1.0)
