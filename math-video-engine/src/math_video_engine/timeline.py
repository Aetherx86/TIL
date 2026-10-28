"""Timeline scheduler and frame orchestrator."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Sequence, Optional
from math_video_engine.animations.base import Animation, Wait
from math_video_engine.objects.base import MObject


@dataclass
class TimelineSegment:
    """A segment of simultaneous animations occurring over [start_time, end_time]."""
    start_time: float
    duration: float
    animations: List[Animation] = field(default_factory=list)

    @property
    def end_time(self) -> float:
        return self.start_time + self.duration


class Timeline:
    """Manages sequencing of animation segments and frame-by-frame progress."""

    def __init__(self):
        self.segments: List[TimelineSegment] = []
        self.current_time: float = 0.0

    def add_segment(self, animations: Sequence[Animation], run_time: Optional[float] = None) -> TimelineSegment:
        """Enqueue parallel animations into the timeline at the current head."""
        anim_list = list(animations)
        if not anim_list:
            anim_list = [Wait(1.0)]

        dur = run_time if run_time is not None else max(a.run_time for a in anim_list)
        for a in anim_list:
            a.run_time = dur

        segment = TimelineSegment(start_time=self.current_time, duration=dur, animations=anim_list)
        self.segments.append(segment)
        self.current_time += dur
        return segment

    def get_total_duration(self) -> float:
        """Total duration of all scheduled segments in seconds."""
        if not self.segments:
            return 0.0
        return self.segments[-1].end_time

    def get_active_segment_and_alpha(self, t: float) -> Optional[Tuple[TimelineSegment, float]]:
        """Find the segment active at time t and return (segment, normalized_alpha)."""
        t = max(0.0, min(self.get_total_duration(), t))
        for seg in self.segments:
            if seg.start_time <= t <= seg.end_time:
                alpha = 1.0 if seg.duration == 0 else (t - seg.start_time) / seg.duration
                return seg, max(0.0, min(1.0, alpha))
        if self.segments:
            last = self.segments[-1]
            return last, 1.0
        return None
