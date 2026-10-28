"""Base Scene architecture for mathematical animations."""

from __future__ import annotations
import os
from typing import List, Optional, Iterator, Sequence
from PIL import Image

from math_video_engine.config import RenderConfig
from math_video_engine.camera import Camera
from math_video_engine.renderer import Renderer
from math_video_engine.objects.base import MObject
from math_video_engine.animations.base import Animation, Wait
from math_video_engine.timeline import Timeline, TimelineSegment


class Scene:
    """Base class for all mathematical video scenes."""

    def __init__(self, config: Optional[RenderConfig] = None):
        self.config = config or RenderConfig.from_preset("720p")
        self.camera = Camera(
            pixel_width=self.config.width,
            pixel_height=self.config.height,
            frame_width=self.config.frame_width,
            frame_height=self.config.frame_height,
        )
        self.renderer = Renderer(self.camera, self.config)
        self.mobjects: List[MObject] = []
        self.timeline = Timeline()
        self._is_constructed = False

    def setup(self) -> None:
        """Lifecycle hook called immediately before construct."""
        pass

    def construct(self) -> None:
        """Primary method to define objects and animations. Must be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement construct().")

    def add(self, *mobjects: MObject) -> Scene:
        """Add mathematical objects to the scene canvas."""
        for m in mobjects:
            if m not in self.mobjects:
                self.mobjects.append(m)
        return self

    def remove(self, *mobjects: MObject) -> Scene:
        """Remove mathematical objects from the scene canvas."""
        for m in mobjects:
            if m in self.mobjects:
                self.mobjects.remove(m)
        return self

    def play(self, *animations: Animation, run_time: Optional[float] = None) -> None:
        """Schedule one or more simultaneous animations onto the timeline."""
        # Ensure animated mobjects are present in the scene
        for anim in animations:
            if anim.mobject not in self.mobjects and anim.mobject.visible:
                self.mobjects.append(anim.mobject)
        self.timeline.add_segment(animations, run_time=run_time)

    def wait(self, duration: float = 1.0) -> None:
        """Schedule a static pause in the timeline."""
        self.timeline.add_segment([Wait(run_time=duration)], run_time=duration)

    def prepare(self) -> None:
        """Construct scene if not already built."""
        if not self._is_constructed:
            self.setup()
            self.construct()
            self._is_constructed = True

    def get_total_duration(self) -> float:
        """Return total running time of the scene in seconds."""
        self.prepare()
        return self.timeline.get_total_duration()

    def generate_frames(self, fps: Optional[int] = None) -> Iterator[Image.Image]:
        """Generator yielding PIL Image frames at the requested frame rate."""
        self.prepare()
        frame_rate = fps or self.config.fps
        total_duration = self.get_total_duration()
        total_frames = max(1, int(round(total_duration * frame_rate)))

        # Timeline playback cursor state
        current_segment_idx = 0
        active_segment: Optional[TimelineSegment] = None

        if self.timeline.segments:
            active_segment = self.timeline.segments[0]
            for anim in active_segment.animations:
                anim.begin()

        dt = 1.0 / frame_rate

        for frame_idx in range(total_frames):
            current_time = frame_idx * dt

            # Transition between timeline segments
            while (
                active_segment is not None
                and current_time > active_segment.end_time
                and current_segment_idx + 1 < len(self.timeline.segments)
            ):
                for anim in active_segment.animations:
                    anim.finish()
                current_segment_idx += 1
                active_segment = self.timeline.segments[current_segment_idx]
                for anim in active_segment.animations:
                    anim.begin()

            # Interpolate active segment
            if active_segment is not None:
                seg_time = current_time - active_segment.start_time
                alpha = 1.0 if active_segment.duration <= 0 else seg_time / active_segment.duration
                for anim in active_segment.animations:
                    anim.update(alpha)

            # Apply updaters on all active mobjects
            for m in self.mobjects:
                m.update(dt)

            # Render current frame
            frame = self.renderer.render_frame(self.mobjects)
            yield frame

        # Finish final segment
        if active_segment is not None:
            for anim in active_segment.animations:
                anim.finish()
