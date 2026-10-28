"""Neural Network and Deep Learning Scenes."""

from __future__ import annotations
import numpy as np
from math_video_engine.scenes.base import Scene
from math_video_engine.objects.coordinate_plane import NumberPlane
from math_video_engine.objects.neural import NeuralNetworkMObject
from math_video_engine.objects.geometry import Circle, Dot, Line
from math_video_engine.objects.text import Text, MathLabel
from math_video_engine.animations.base import FadeIn, FadeOut, Wait
from math_video_engine.animations.transform import Create
from math_video_engine.animations.movement import Shift
from math_video_engine.colors import BLUE, YELLOW, GREEN, RED, WHITE, GOLD


class NeuralNetworkArchitectureScene(Scene):
    """Visualizes multi-layer feedforward network and signal activation flow."""

    def construct(self) -> None:
        title = Text("Neural Networks: Deep Feedforward Architecture", point=(0.0, 3.4), font_size=24, color=WHITE)
        subtitle = MathLabel("a^(L) = sigma(W * a^(L-1) + b)", point=(0.0, 2.8), color=GOLD)

        network = NeuralNetworkMObject(
            layer_sizes=[3, 4, 4, 2],
            layer_spacing=2.6,
            neuron_spacing=1.1,
            center=(0.0, -0.4)
        )
        self.add(title, subtitle, network)

        layer_labels = [
            Text("Input", point=(-3.9, -2.5), font_size=18, color=WHITE),
            Text("Hidden 1", point=(-1.3, -2.5), font_size=18, color=WHITE),
            Text("Hidden 2", point=(1.3, -2.5), font_size=18, color=WHITE),
            Text("Output", point=(3.9, -2.5), font_size=18, color=WHITE),
        ]
        for lbl in layer_labels:
            self.add(lbl)

        self.wait(0.5)

        # Pulse activation forward across layers
        self.play(FadeIn(layer_labels[0]), run_time=0.5)
        network.set_layer_activation(0, [0.9, 0.2, 0.8])
        self.wait(0.6)

        network.set_layer_activation(1, [0.7, 0.95, 0.4, 0.85])
        self.wait(0.6)

        network.set_layer_activation(2, [0.6, 0.3, 0.9, 0.75])
        self.wait(0.6)

        network.set_layer_activation(3, [0.15, 0.98])
        res_label = Text("Classification: Class 1 (98% confidence)", point=(0.0, -3.2), font_size=20, color=GREEN)
        self.play(FadeIn(res_label), run_time=0.8)
        self.wait(1.0)


class GradientDescentOptimizationScene(Scene):
    """Visualizes parameter optimization descending a 2D loss landscape."""

    def construct(self) -> None:
        title = Text("Gradient Descent: Minimizing Cost Function", point=(0.0, 3.4), font_size=24, color=WHITE)
        formula = MathLabel("w_(t+1) = w_t - eta * Grad(Loss)", point=(0.0, 2.8), color=YELLOW)

        plane = NumberPlane()
        self.add(plane, title, formula)

        # Draw concentric loss contours around minimum at (1.0, 0.5)
        min_center = (1.0, 0.5)
        for r in [0.6, 1.2, 1.8, 2.5, 3.2]:
            contour = Circle(
                radius=r,
                center=min_center,
                color="#2a3c54",
                stroke_width=1.5
            )
            self.add(contour)

        target_star = Dot(point=min_center, radius=0.1, color=GREEN)
        target_label = MathLabel("Global Minimum", point=(1.0, -0.1), color=GREEN)
        self.add(target_star, target_label)

        # Trajectory points
        steps = [
            (-3.5, 2.8),
            (-2.0, 1.8),
            (-0.8, 1.2),
            (0.2, 0.8),
            (0.7, 0.6),
            (1.0, 0.5),
        ]

        agent = Dot(point=steps[0], radius=0.12, color=RED)
        self.add(agent)
        self.wait(0.5)

        # Animate descent trajectory
        for i in range(len(steps) - 1):
            p_start = steps[i]
            p_end = steps[i + 1]
            step_line = Line(start=p_start, end=p_end, color=YELLOW, stroke_width=2.5)
            self.play(
                Create(step_line),
                Shift(agent, vector=(p_end[0] - p_start[0], p_end[1] - p_start[1])),
                run_time=0.6
            )
        self.wait(1.0)
