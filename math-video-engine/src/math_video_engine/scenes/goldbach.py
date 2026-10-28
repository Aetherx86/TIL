"""Goldbach Conjecture Visualizations: Strong and Weak Conjectures."""

from __future__ import annotations
import math
import numpy as np
from typing import List, Tuple

from math_video_engine.scenes.base import Scene
from math_video_engine.objects.coordinate_plane import NumberPlane
from math_video_engine.objects.geometry import Dot, Line, Arc, Circle, Rectangle
from math_video_engine.objects.function_graph import ParametricCurve
from math_video_engine.objects.text import Text, MathLabel
from math_video_engine.animations.base import FadeIn, FadeOut, Wait
from math_video_engine.animations.transform import Create, Transform
from math_video_engine.colors import (
    BLUE, YELLOW, GREEN, RED, GOLD, WHITE, PURPLE, GRAY_C, GRAY_D, TEAL
)


def is_prime(n: int) -> bool:
    """Primality test."""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    w = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += w
        w = 6 - w
    return True


def get_primes_up_to(limit: int) -> List[int]:
    """Return list of prime numbers up to limit."""
    return [p for p in range(2, limit + 1) if is_prime(p)]


def goldbach_pairs(even_n: int) -> List[Tuple[int, int]]:
    """Return all prime pairs (p1, p2) with p1 <= p2 such that p1 + p2 == even_n."""
    pairs = []
    primes = get_primes_up_to(even_n)
    prime_set = set(primes)
    for p in primes:
        if p > even_n // 2:
            break
        q = even_n - p
        if q in prime_set:
            pairs.append((p, q))
    return pairs


def ternary_goldbach_triplets(odd_n: int) -> List[Tuple[int, int, int]]:
    """Return prime triplets (p1, p2, p3) with p1 <= p2 <= p3 such that p1 + p2 + p3 == odd_n."""
    triplets = []
    primes = get_primes_up_to(odd_n)
    prime_set = set(primes)
    for i, p1 in enumerate(primes):
        if p1 > odd_n // 3:
            break
        for p2 in primes[i:]:
            p3 = odd_n - p1 - p2
            if p3 < p2:
                break
            if p3 in prime_set:
                triplets.append((p1, p2, p3))
                if len(triplets) >= 4:
                    return triplets
    return triplets


class StrongGoldbachConjectureScene(Scene):
    """Visualizes the Strong (Binary) Goldbach Conjecture: 2n = p1 + p2 for every even 2n > 2."""

    def construct(self) -> None:
        title = Text("Strong Goldbach Conjecture (Euler, 1742)", point=(0.0, 3.4), font_size=24, color=WHITE)
        subtitle = MathLabel("Every even integer 2n > 2 is the sum of two primes: 2n = p1 + p2", point=(0.0, 2.8), color=GOLD)
        status = Text("Status: Unsolved (Verified computationally up to 4 * 10^18)", point=(0.0, 2.3), font_size=18, color=YELLOW)

        self.add(title, subtitle, status)

        # Baseline axis for primes: map [0, 36] to world x in [-5.5, 5.5]
        axis_line = Line(start=(-5.5, -0.2), end=(5.5, -0.2), color=GRAY_C, stroke_width=2.5)
        self.add(axis_line)

        def val_to_x(val: float) -> float:
            return -5.5 + (val / 36.0) * 11.0

        # Draw tick marks and prime markers
        primes_sample = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
        for p in primes_sample:
            px = val_to_x(p)
            tick = Line(start=(px, -0.35), end=(px, -0.05), color=BLUE, stroke_width=2.0)
            dot = Dot(point=(px, -0.2), radius=0.08, color=BLUE)
            lbl = Text(str(p), point=(px, -0.6), font_size=14, color=WHITE)
            self.add(tick, dot, lbl)

        self.wait(0.6)

        # Example 1: 2n = 20 = 3 + 17 = 7 + 13
        target_even = 20
        ex_label = MathLabel(f"Target 2n = {target_even}", point=(-3.5, 1.4), color=YELLOW, font_size=22)
        self.play(FadeIn(ex_label), run_time=0.6)

        pairs_20 = goldbach_pairs(target_even)
        colors_pair = [GREEN, TEAL]
        arcs = []
        labels = []

        for idx, (p1, p2) in enumerate(pairs_20):
            x1 = val_to_x(p1)
            x2 = val_to_x(p2)
            mid_x = (x1 + x2) / 2.0
            radius = (x2 - x1) / 2.0
            col = colors_pair[idx % len(colors_pair)]

            # Semicircular arc connecting prime pair (p1, p2)
            arc = Arc(
                radius=radius,
                start_angle=0.0,
                angle=math.pi,
                center=(mid_x, -0.2),
                color=col,
                stroke_width=3.0,
                num_points=40
            )
            arcs.append(arc)

            pair_lbl = MathLabel(f"{target_even} = {p1} + {p2}", point=(1.0, 1.4 - idx * 0.5), color=col, font_size=18)
            labels.append(pair_lbl)
            self.play(Create(arc), FadeIn(pair_lbl), run_time=0.9)

        self.wait(0.8)

        # Clean up example 1
        for a in arcs:
            self.remove(a)
        for l in labels:
            self.remove(l)
        self.remove(ex_label)

        # Example 2: 2n = 30 = 7 + 23 = 11 + 19 = 13 + 17
        target_even_2 = 30
        ex_label_2 = MathLabel(f"Target 2n = {target_even_2}", point=(-3.5, 1.4), color=YELLOW, font_size=22)
        self.play(FadeIn(ex_label_2), run_time=0.6)

        pairs_30 = goldbach_pairs(target_even_2)
        colors_30 = [GOLD, GREEN, PURPLE]
        for idx, (p1, p2) in enumerate(pairs_30[:3]):
            x1 = val_to_x(p1)
            x2 = val_to_x(p2)
            mid_x = (x1 + x2) / 2.0
            radius = (x2 - x1) / 2.0
            col = colors_30[idx % len(colors_30)]

            arc = Arc(
                radius=radius,
                start_angle=0.0,
                angle=math.pi,
                center=(mid_x, -0.2),
                color=col,
                stroke_width=3.0,
                num_points=40
            )
            pair_lbl = MathLabel(f"{target_even_2} = {p1} + {p2}", point=(1.0, 1.4 - idx * 0.5), color=col, font_size=18)
            self.play(Create(arc), FadeIn(pair_lbl), run_time=0.7)

        # Goldbach comet representation banner
        comet_box = Rectangle(width=10.0, height=1.0, center=(0.0, -2.2), stroke_color=BLUE, fill_color="#141c2c", fill_opacity=0.9)
        comet_text = Text(
            "Goldbach Comet: The number of prime representations g(2n) grows asymptotically with n",
            point=(0.0, -2.2),
            font_size=17,
            color=WHITE
        )
        self.play(Create(comet_box), FadeIn(comet_text), run_time=1.0)
        self.wait(1.0)


class WeakGoldbachConjectureScene(Scene):
    """Visualizes the Weak (Ternary) Goldbach Conjecture: 2n + 1 = p1 + p2 + p3."""

    def construct(self) -> None:
        title = Text("Weak Goldbach Conjecture (Ternary)", point=(0.0, 3.4), font_size=24, color=WHITE)
        subtitle = MathLabel("Every odd integer 2n + 1 > 5 is the sum of three primes: p1 + p2 + p3", point=(0.0, 2.8), color=GOLD)
        proof_status = Text("Status: PROVED by Harald Helfgott (2013)", point=(0.0, 2.3), font_size=18, color=GREEN)

        self.add(title, subtitle, proof_status)

        # Number axis
        axis = Line(start=(-5.5, -0.4), end=(5.5, -0.4), color=GRAY_C, stroke_width=2.5)
        self.add(axis)

        def val_to_x(val: float) -> float:
            return -5.5 + (val / 38.0) * 11.0

        for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
            px = val_to_x(p)
            dot = Dot(point=(px, -0.4), radius=0.08, color=BLUE)
            lbl = Text(str(p), point=(px, -0.8), font_size=14, color=WHITE)
            self.add(dot, lbl)

        self.wait(0.6)

        # Demonstrate odd number 27 = 3 + 5 + 19 = 7 + 7 + 13
        target_odd = 27
        target_lbl = MathLabel(f"Odd Target: {target_odd}", point=(-3.5, 1.4), color=YELLOW, font_size=22)
        self.play(FadeIn(target_lbl), run_time=0.6)

        triplets = ternary_goldbach_triplets(target_odd)

        for idx, (p1, p2, p3) in enumerate(triplets[:2]):
            col = GREEN if idx == 0 else TEAL
            decomp_lbl = MathLabel(f"{target_odd} = {p1} + {p2} + {p3}", point=(0.5, 1.4 - idx * 0.6), color=col, font_size=20)

            # Draw two chained arcs: p1 -> p1+p2 -> p1+p2+p3
            x0 = val_to_x(0)
            x1 = val_to_x(p1)
            x2 = val_to_x(p1 + p2)
            x3 = val_to_x(target_odd)

            arc1 = Arc(radius=(x1 - x0)/2.0, start_angle=0.0, angle=math.pi, center=((x0 + x1)/2.0, -0.4), color=col, stroke_width=2.5)
            arc2 = Arc(radius=(x2 - x1)/2.0, start_angle=0.0, angle=math.pi, center=((x1 + x2)/2.0, -0.4), color=col, stroke_width=2.5)
            arc3 = Arc(radius=(x3 - x2)/2.0, start_angle=0.0, angle=math.pi, center=((x2 + x3)/2.0, -0.4), color=col, stroke_width=2.5)

            self.play(FadeIn(decomp_lbl), Create(arc1), Create(arc2), Create(arc3), run_time=1.2)

        self.wait(0.8)

        # Relationship banner: Strong implies Weak
        implication_box = Rectangle(width=11.0, height=1.2, center=(0.0, -2.4), stroke_color=GOLD, fill_color="#1a2233", fill_opacity=0.9)
        imp_line1 = Text("Theorem: Strong Goldbach Conjecture directly implies the Weak Conjecture", point=(0.0, -2.15), font_size=17, color=WHITE)
        imp_line2 = Text("If (2n - 3) = p1 + p2 (even), then (2n) + 1 = 3 + p1 + p2 (odd).", point=(0.0, -2.65), font_size=15, color=GOLD)

        self.play(Create(implication_box), FadeIn(imp_line1), FadeIn(imp_line2), run_time=1.2)
        self.wait(1.0)
