"""Mathematical visual objects package."""

from math_video_engine.objects.base import MObject, VGroup
from math_video_engine.objects.geometry import (
    Dot, Line, Arrow, Rectangle, Square, Circle, Arc, Polygon
)
from math_video_engine.objects.coordinate_plane import (
    NumberLine, CoordinateAxes, NumberPlane
)
from math_video_engine.objects.vector import Vector, BasisVectors
from math_video_engine.objects.function_graph import (
    ParametricCurve, FunctionGraph, RiemannRectangles, TangentLine
)
from math_video_engine.objects.text import Text, MathLabel
from math_video_engine.objects.neural import NeuralNetworkMObject

__all__ = [
    "MObject",
    "VGroup",
    "Dot",
    "Line",
    "Arrow",
    "Rectangle",
    "Square",
    "Circle",
    "Arc",
    "Polygon",
    "NumberLine",
    "CoordinateAxes",
    "NumberPlane",
    "Vector",
    "BasisVectors",
    "ParametricCurve",
    "FunctionGraph",
    "RiemannRectangles",
    "TangentLine",
    "Text",
    "MathLabel",
    "NeuralNetworkMObject",
]
