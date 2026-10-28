"""Command-line interface for Math Video Engine."""

from __future__ import annotations
import argparse
import sys
import os
import time
from typing import Optional, List

from math_video_engine.config import RenderConfig, RESOLUTION_PRESETS
from math_video_engine.scenes import SCENE_REGISTRY, get_scene_class, list_available_scenes
from math_video_engine.encoders import export_video, is_ffmpeg_available


def print_scene_table() -> None:
    """Print an aligned tabular list of all available mathematical scenes."""
    scenes = list_available_scenes()
    header = f"{'Scene Name':<34} | {'Category':<18} | {'Description'}"
    separator = "-" * len(header) + "-" * 20
    print(header)
    print(separator)
    for s in scenes:
        print(f"{s['name']:<34} | {s['category']:<18} | {s['description']}")
    print(f"\nTotal registered scenes: {len(scenes)}")


def cmd_list(args: argparse.Namespace) -> int:
    """Handle 'list' subcommand."""
    print("Math Video Engine - Available Mathematical Scenes Catalog\n")
    print_scene_table()
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    """Handle 'render' subcommand."""
    try:
        scene_cls = get_scene_class(args.scene)
    except KeyError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    config = RenderConfig.from_preset(
        preset=args.preset,
        fps=args.fps,
        output_dir=args.output_dir
    )
    scene = scene_cls(config=config)

    print(f"Preparing scene '{args.scene}'...")
    duration = scene.get_total_duration()
    total_frames = int(round(duration * config.fps))
    print(f"Resolution: {config.width}x{config.height} ({args.preset})")
    print(f"Frame Rate: {config.fps} FPS")
    print(f"Duration:   {duration:.2f} seconds ({total_frames} frames)")
    print(f"Format:     {args.format}")

    start_time = time.time()
    try:
        output_path = export_video(
            scene=scene,
            output_path=args.output,
            output_format=args.format,
            fps=config.fps
        )
        elapsed = time.time() - start_time
        print(f"Successfully rendered to: {output_path}")
        print(f"Elapsed time: {elapsed:.2f}s ({total_frames / max(0.001, elapsed):.1f} fps)")
        return 0
    except Exception as e:
        print(f"Render failed: {e}", file=sys.stderr)
        return 1


def cmd_render_all(args: argparse.Namespace) -> int:
    """Handle 'render-all' subcommand."""
    scenes = list(SCENE_REGISTRY.keys())
    print(f"Batch rendering {len(scenes)} scenes in preset '{args.preset}' ({args.format})...\n")

    os.makedirs(args.output_dir, exist_ok=True)
    success_count = 0

    for idx, name in enumerate(scenes, start=1):
        print(f"[{idx}/{len(scenes)}] Rendering {name}...")
        scene_cls = SCENE_REGISTRY[name]
        config = RenderConfig.from_preset(preset=args.preset, fps=args.fps, output_dir=args.output_dir)
        scene = scene_cls(config=config)
        try:
            out_file = export_video(scene, output_format=args.format, fps=config.fps)
            print(f"       -> Done: {os.path.basename(out_file)}")
            success_count += 1
        except Exception as e:
            print(f"       -> Failed: {e}", file=sys.stderr)

    print(f"\nBatch render complete: {success_count}/{len(scenes)} scenes succeeded.")
    return 0 if success_count == len(scenes) else 1


def cmd_inspect(args: argparse.Namespace) -> int:
    """Handle 'inspect' subcommand."""
    try:
        scene_cls = get_scene_class(args.scene)
    except KeyError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    scene = scene_cls()
    duration = scene.get_total_duration()
    print(f"Scene:             {scene_cls.__name__}")
    print(f"Total Duration:    {duration:.2f}s")
    print(f"Timeline Segments: {len(scene.timeline.segments)}")
    print(f"Objects in Canvas: {len(scene.mobjects)}")
    for idx, seg in enumerate(scene.timeline.segments, start=1):
        anim_names = [a.__class__.__name__ for a in seg.animations]
        print(f"  Segment {idx}: start={seg.start_time:.2f}s, dur={seg.duration:.2f}s, anims={anim_names}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="math-video-engine",
        description="Mathematical animation and video generation engine recreating core visual mathematics concepts."
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # list
    subparsers.add_parser("list", help="List all available recreated mathematical scenes")

    # render
    render_parser = subparsers.add_parser("render", help="Render a specific mathematical scene")
    render_parser.add_argument("scene", help="Class name of the scene to render")
    render_parser.add_argument("--format", choices=["mp4", "gif", "webp", "frames"], default="mp4", help="Output file format")
    render_parser.add_argument("--preset", choices=list(RESOLUTION_PRESETS.keys()), default="720p", help="Resolution preset")
    render_parser.add_argument("--fps", type=int, default=30, help="Frames per second")
    render_parser.add_argument("--output", "-o", default=None, help="Explicit output destination path")
    render_parser.add_argument("--output-dir", default="output", help="Directory for rendered output")

    # render-all
    all_parser = subparsers.add_parser("render-all", help="Batch render all mathematical scenes")
    all_parser.add_argument("--format", choices=["mp4", "gif", "webp", "frames"], default="mp4", help="Output format")
    all_parser.add_argument("--preset", choices=list(RESOLUTION_PRESETS.keys()), default="preview", help="Resolution preset")
    all_parser.add_argument("--fps", type=int, default=20, help="Frames per second")
    all_parser.add_argument("--output-dir", default="output", help="Directory for rendered outputs")

    # inspect
    inspect_parser = subparsers.add_parser("inspect", help="Inspect timeline structure and metadata of a scene")
    inspect_parser.add_argument("scene", help="Class name of the scene to inspect")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.subcommand is None:
        parser.print_help()
        return 0

    if args.subcommand == "list":
        return cmd_list(args)
    elif args.subcommand == "render":
        return cmd_render(args)
    elif args.subcommand == "render-all":
        return cmd_render_all(args)
    elif args.subcommand == "inspect":
        return cmd_inspect(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
