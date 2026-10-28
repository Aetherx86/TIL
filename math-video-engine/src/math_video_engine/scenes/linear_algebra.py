"""Linear Algebra Video Scenes inspired by Essence of Linear Algebra."""

from __future__ import annotations
import numpy as np
from math_video_engine.scenes.base import Scene
from math_video_engine.objects.coordinate_plane import NumberPlane
from math_video_engine.objects.vector import Vector, BasisVectors
from math_video_engine.objects.geometry import Polygon, Dot, Line
from math_video_engine.objects.text import Text, MathLabel
from math_video_engine.animations.base import FadeIn, FadeOut, Wait
from math_video_engine.animations.transform import Create
from math_video_engine.animations.movement import Shift
from math_video_engine.animations.matrix import ApplyMatrix
from math_video_engine.colors import (
    GREEN, RED, YELLOW, BLUE, WHITE, GOLD, PURPLE, BLUE_D
)


class VectorLinearCombinationScene(Scene):
    """Visualizes vector addition and span: v = 2*i_hat + 3*j_hat."""

    def construct(self) -> None:
        title = Text("Essence of Linear Algebra: Linear Combinations", point=(0.0, 3.4), font_size=24, color=WHITE)
        plane = NumberPlane()
        self.add(plane, title)

        # Basis vectors
        basis = BasisVectors(i_color=GREEN, j_color=RED)
        i_label = MathLabel("i-hat", point=(1.2, -0.4), color=GREEN)
        j_label = MathLabel("j-hat", point=(-0.6, 1.2), color=RED)

        self.play(Create(basis.i_hat), Create(basis.j_hat), FadeIn(i_label), FadeIn(j_label), run_time=1.5)
        self.wait(0.5)

        # Scale basis vectors
        v1 = Vector(coords=(2.0, 0.0), color=GREEN, stroke_width=4.0)
        v2 = Vector(coords=(0.0, 3.0), tail=(2.0, 0.0), color=RED, stroke_width=4.0)
        v_sum = Vector(coords=(2.0, 3.0), color=YELLOW, stroke_width=5.0)

        sum_label = MathLabel("v = 2*i + 3*j", point=(2.4, 3.4), color=YELLOW)

        self.play(Create(v1), run_time=1.0)
        self.play(Create(v2), run_time=1.0)
        self.play(Create(v_sum), FadeIn(sum_label), run_time=1.5)
        self.wait(1.0)


class MatrixTransformationScene(Scene):
    """Visualizes linear transformation via grid deformation with matrix [[2, 1], [0, 1.5]]."""

    def construct(self) -> None:
        title = Text("Linear Transformations as Coordinate Grid Warping", point=(0.0, 3.4), font_size=24, color=WHITE)
        matrix_label = MathLabel("Matrix A = [[2.0, 1.0], [0.0, 1.5]]", point=(0.0, 2.8), color=YELLOW)

        plane = NumberPlane()
        basis = BasisVectors(i_color=GREEN, j_color=RED)
        self.add(plane, title, matrix_label, basis)

        self.wait(0.8)

        # Apply transformation matrix
        transformation_matrix = [[2.0, 1.0], [0.0, 1.5]]
        self.play(
            ApplyMatrix(plane, transformation_matrix, run_time=2.5),
            ApplyMatrix(basis, transformation_matrix, run_time=2.5),
        )
        self.wait(1.0)


class DeterminantAreaScene(Scene):
    """Visualizes the geometric meaning of determinant as signed area scaling factor."""

    def construct(self) -> None:
        title = Text("Determinant: Area Scaling Factor", point=(0.0, 3.4), font_size=24, color=WHITE)
        det_calc = MathLabel("det([[2, 1], [0, 1.5]]) = 2*1.5 - 1*0 = 3.0", point=(0.0, 2.8), color=GOLD)

        plane = NumberPlane()
        self.add(plane, title, det_calc)

        # Unit square before transformation (Area = 1)
        unit_square = Polygon(
            vertices=[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]],
            stroke_color=YELLOW,
            stroke_width=3.0,
            fill_color=YELLOW,
            fill_opacity=0.35,
            z_index=3
        )
        area_label_before = Text("Initial Area = 1.0", point=(0.5, 0.5), color=WHITE, font_size=18)
        self.add(unit_square, area_label_before)
        self.wait(0.8)

        # Transformation
        matrix = [[2.0, 1.0], [0.0, 1.5]]
        transformed_square = Polygon(
            vertices=[[0.0, 0.0], [2.0, 0.0], [3.0, 1.5], [1.0, 1.5]],
            stroke_color=YELLOW,
            stroke_width=3.0,
            fill_color=YELLOW,
            fill_opacity=0.45,
            z_index=3
        )
        area_label_after = Text("Scaled Area = 3.0", point=(1.5, 0.75), color=WHITE, font_size=18)

        self.play(
            FadeOut(area_label_before),
            ApplyMatrix(plane, matrix, run_time=2.0),
            ApplyMatrix(unit_square, matrix, run_time=2.0),
        )
        self.play(FadeIn(area_label_after), run_time=0.8)
        self.wait(1.0)


class EigenvectorTransformationScene(Scene):
    """Visualizes eigenvectors maintaining their span under a linear map."""

    def construct(self) -> None:
        title = Text("Eigenvectors: Directions That Only Scale", point=(0.0, 3.4), font_size=24, color=WHITE)
        formula = MathLabel("A*v = lambda*v (Span remains invariant)", point=(0.0, 2.8), color=GREEN)

        plane = NumberPlane()
        self.add(plane, title, formula)

        # Diagonal matrix: x stretches by 2.0, y stretches by 0.5
        # Eigenvectors are along the axes
        eigen_x = Vector(coords=(1.5, 0.0), color=GREEN, stroke_width=4.5)
        eigen_y = Vector(coords=(0.0, 1.5), color=GREEN, stroke_width=4.5)
        arbitrary_v = Vector(coords=(1.2, 1.2), color=RED, stroke_width=4.0)

        x_span = Line(start=(-6.0, 0.0), end=(6.0, 0.0), color=GREEN, stroke_width=1.5)
        y_span = Line(start=(0.0, -3.5), end=(0.0, 3.5), color=GREEN, stroke_width=1.5)

        self.add(x_span, y_span, eigen_x, eigen_y, arbitrary_v)
        self.wait(0.8)

        mat = [[2.0, 0.0], [0.0, 0.5]]
        self.play(
            ApplyMatrix(plane, mat, run_time=2.2),
            ApplyMatrix(eigen_x, mat, run_time=2.2),
            ApplyMatrix(eigen_y, mat, run_time=2.2),
            ApplyMatrix(arbitrary_v, mat, run_time=2.2),
        )
        self.wait(1.0)
