"""Unit tests for the CLI interface."""

import pytest
from math_video_engine.cli import main


def test_cli_list(capsys):
    ret = main(["list"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "VectorLinearCombinationScene" in captured.out
    assert "FourierEpicyclesScene" in captured.out


def test_cli_inspect(capsys):
    ret = main(["inspect", "MatrixTransformationScene"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Scene:             MatrixTransformationScene" in captured.out
    assert "Total Duration:" in captured.out


def test_cli_inspect_invalid_scene(capsys):
    ret = main(["inspect", "UnknownScene"])
    assert ret == 1
    captured = capsys.readouterr()
    assert "Error:" in captured.err


def test_cli_render(tmp_path):
    out_file = str(tmp_path / "cli_test.gif")
    ret = main([
        "render",
        "VectorLinearCombinationScene",
        "--preset", "preview",
        "--fps", "10",
        "--format", "gif",
        "--output", out_file,
    ])
    assert ret == 0


def test_cli_render_invalid_scene(capsys):
    ret = main(["render", "InvalidScene"])
    assert ret == 1
