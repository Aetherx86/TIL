"""Integration tests for all registered mathematical video scenes."""

import pytest
from math_video_engine.config import RenderConfig
from math_video_engine.scenes import SCENE_REGISTRY, get_scene_class, list_available_scenes


@pytest.mark.parametrize("scene_name,scene_cls", list(SCENE_REGISTRY.items()))
def test_scene_construction_and_duration(scene_name, scene_cls):
    config = RenderConfig.from_preset("preview", fps=10)
    scene = scene_cls(config=config)
    duration = scene.get_total_duration()
    assert duration > 0.0, f"Scene '{scene_name}' must have positive duration"
    assert len(scene.timeline.segments) > 0, f"Scene '{scene_name}' must have timeline segments"


@pytest.mark.parametrize("scene_name,scene_cls", list(SCENE_REGISTRY.items()))
def test_scene_frame_generation(scene_name, scene_cls):
    config = RenderConfig.from_preset("preview", fps=5)
    scene = scene_cls(config=config)
    # Generate first 3 frames to verify rasterization pipeline
    frames_generated = 0
    for frame in scene.generate_frames(fps=5):
        assert frame.size == (config.width, config.height)
        assert frame.mode == "RGBA"
        frames_generated += 1
        if frames_generated >= 3:
            break
    assert frames_generated >= 3


def test_get_scene_class_valid():
    cls = get_scene_class("vectorlinearcombinationscene")
    assert cls.__name__ == "VectorLinearCombinationScene"


def test_get_scene_class_invalid():
    with pytest.raises(KeyError):
        get_scene_class("NonExistentSceneName")


def test_list_available_scenes_catalog():
    catalog = list_available_scenes()
    assert len(catalog) == len(SCENE_REGISTRY)
    for entry in catalog:
        assert "name" in entry
        assert "category" in entry
        assert "description" in entry
