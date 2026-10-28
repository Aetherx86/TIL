"""Math Video Engine: Standalone Mathematical Animation & Video Generation Library."""

from math_video_engine.config import RenderConfig, RESOLUTION_PRESETS
from math_video_engine.camera import Camera
from math_video_engine.renderer import Renderer
from math_video_engine.colors import *
from math_video_engine.easing import *
from math_video_engine.objects import *
from math_video_engine.animations import *
from math_video_engine.scenes import Scene, SCENE_REGISTRY, get_scene_class, list_available_scenes
from math_video_engine.encoders import export_video

__version__ = "0.1.0"
__author__ = "Jeonghoon Kim <jk9576@hanyang.ac.kr>"
