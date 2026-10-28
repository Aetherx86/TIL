"""Unit tests for timeline scheduling and segment tracking."""

import pytest
from math_video_engine.timeline import Timeline
from math_video_engine.animations.base import Wait


def test_timeline_duration():
    tl = Timeline()
    assert tl.get_total_duration() == 0.0

    tl.add_segment([Wait(1.5)])
    assert tl.get_total_duration() == 1.5

    tl.add_segment([Wait(2.0)])
    assert tl.get_total_duration() == 3.5


def test_timeline_active_segment_lookup():
    tl = Timeline()
    seg1 = tl.add_segment([Wait(1.0)])
    seg2 = tl.add_segment([Wait(2.0)])

    res_0 = tl.get_active_segment_and_alpha(0.5)
    assert res_0 is not None
    assert res_0[0] == seg1
    assert pytest.approx(res_0[1], abs=1e-5) == 0.5

    res_1 = tl.get_active_segment_and_alpha(2.0)
    assert res_1 is not None
    assert res_1[0] == seg2
    assert pytest.approx(res_1[1], abs=1e-5) == 0.5
