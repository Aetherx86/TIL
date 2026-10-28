"""Unit tests for easing and rate functions."""

import pytest
from math_video_engine.easing import (
    linear, smooth, ease_in_quad, ease_out_quad, ease_in_out_cubic,
    there_and_back, rush_into, rush_from
)


def test_easing_boundaries():
    funcs = [linear, smooth, ease_in_quad, ease_out_quad, ease_in_out_cubic]
    for fn in funcs:
        assert pytest.approx(fn(0.0), abs=1e-5) == 0.0
        assert pytest.approx(fn(1.0), abs=1e-5) == 1.0


def test_smooth_monotonic():
    ts = [i / 20.0 for i in range(21)]
    vals = [smooth(t) for t in ts]
    for i in range(len(vals) - 1):
        assert vals[i] <= vals[i + 1]


def test_there_and_back():
    assert pytest.approx(there_and_back(0.0), abs=1e-5) == 0.0
    assert pytest.approx(there_and_back(0.5), abs=1e-5) == 1.0
    assert pytest.approx(there_and_back(1.0), abs=1e-5) == 0.0
