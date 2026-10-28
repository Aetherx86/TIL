"""Animation system package."""

from math_video_engine.animations.base import Animation, Wait, FadeIn, FadeOut
from math_video_engine.animations.movement import Shift, Rotate, Scale
from math_video_engine.animations.transform import Create, Transform
from math_video_engine.animations.matrix import ApplyMatrix

__all__ = [
    "Animation",
    "Wait",
    "FadeIn",
    "FadeOut",
    "Shift",
    "Rotate",
    "Scale",
    "Create",
    "Transform",
    "ApplyMatrix",
]
