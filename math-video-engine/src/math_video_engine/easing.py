"""Animation rate and easing functions."""

from __future__ import annotations
import math
from typing import Callable

RateFunc = Callable[[float], float]


def linear(t: float) -> float:
    """Linear progression."""
    return t


def smooth(t: float, inflection: float = 10.0) -> float:
    """Classic smooth-step / sigmoid-style easing with zero derivative at endpoints."""
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def ease_in_quad(t: float) -> float:
    """Quadratic acceleration from zero velocity."""
    t = max(0.0, min(1.0, t))
    return t * t


def ease_out_quad(t: float) -> float:
    """Quadratic deceleration to zero velocity."""
    t = max(0.0, min(1.0, t))
    return t * (2.0 - t)


def ease_in_out_cubic(t: float) -> float:
    """Cubic acceleration and deceleration."""
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        return 4.0 * t * t * t
    p = 2.0 * t - 2.0
    return 0.5 * p * p * p + 1.0


def rush_into(t: float, inflection: float = 2.0) -> float:
    """Accelerate rapidly into the end state."""
    t = max(0.0, min(1.0, t))
    return 2.0 * smooth(0.5 * t)


def rush_from(t: float, inflection: float = 2.0) -> float:
    """Start fast and smoothly come to a halt."""
    t = max(0.0, min(1.0, t))
    return 2.0 * smooth(0.5 * (t + 1.0)) - 1.0


def there_and_back(t: float) -> float:
    """Ramp smoothly from 0 to 1 and back to 0."""
    t = max(0.0, min(1.0, t))
    return 1.0 - abs(2.0 * t - 1.0)


def bounce(t: float) -> float:
    """Bouncing decay easing."""
    t = max(0.0, min(1.0, t))
    if t < (1.0 / 2.75):
        return 7.5625 * t * t
    elif t < (2.0 / 2.75):
        t -= 1.5 / 2.75
        return 7.5625 * t * t + 0.75
    elif t < (2.5 / 2.75):
        t -= 2.25 / 2.75
        return 7.5625 * t * t + 0.9375
    else:
        t -= 2.625 / 2.75
        return 7.5625 * t * t + 0.984375


def wiggle(t: float, wiggles: int = 2) -> float:
    """Oscillate smoothly around 0 before resting."""
    t = max(0.0, min(1.0, t))
    return math.sin(wiggles * 2.0 * math.pi * t) * (1.0 - t)
