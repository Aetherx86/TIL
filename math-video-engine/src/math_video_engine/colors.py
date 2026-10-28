"""Color palette and color utility functions."""

from __future__ import annotations
from typing import Tuple, List, Union

# Core 3Blue1Brown inspired palette
BLUE_A = "#C7E9F1"
BLUE_B = "#9CDCEB"
BLUE_C = "#58C4DD"
BLUE_D = "#29ABCA"
BLUE_E = "#1C758A"
BLUE = "#58C4DD"

TEAL_A = "#ACEAD7"
TEAL_B = "#76DDC0"
TEAL_C = "#5CD0B3"
TEAL_D = "#36AC98"
TEAL_E = "#208573"
TEAL = "#5CD0B3"

GREEN_A = "#C9E2AE"
GREEN_B = "#A6CF8C"
GREEN_C = "#83C167"
GREEN_D = "#77B05D"
GREEN_E = "#5C8C4B"
GREEN = "#83C167"

YELLOW_A = "#FFF1B6"
YELLOW_B = "#FFEA94"
YELLOW_C = "#FFFF00"
YELLOW_D = "#F4D345"
YELLOW_E = "#E8C11C"
YELLOW = "#FFFF00"
GOLD = "#F4D345"

RED_A = "#F7C1C6"
RED_B = "#F399A2"
RED_C = "#EB5766"
RED_D = "#CF3F4D"
RED_E = "#A72C38"
RED = "#EB5766"

PURPLE_A = "#CAA3E8"
PURPLE_B = "#9B72CF"
PURPLE_C = "#7048B5"
PURPLE_D = "#542F99"
PURPLE_E = "#391B77"
PURPLE = "#9B72CF"

PINK_A = "#F9C0D9"
PINK_B = "#F494BE"
PINK_C = "#EC68A2"
PINK_D = "#CA4B84"
PINK_E = "#A12E65"
PINK = "#EC68A2"

ORANGE_A = "#FFD0A8"
ORANGE_B = "#FFB270"
ORANGE_C = "#FF8D3B"
ORANGE_D = "#E5681E"
ORANGE_E = "#BC4405"
ORANGE = "#FF8D3B"

WHITE = "#FFFFFF"
GRAY_A = "#DDDDDD"
GRAY_B = "#BBBBBB"
GRAY_C = "#888888"
GRAY_D = "#555555"
GRAY_E = "#222222"
GRAY = "#888888"
DARK_GRAY = "#333333"
BLACK = "#000000"
DARK_BLUE = "#141824"


def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    """Convert hex color string (#RRGGBB or #RGB) to (R, G, B) tuple in 0..255."""
    clean = hex_code.lstrip("#")
    if len(clean) == 3:
        clean = "".join(c * 2 for c in clean)
    if len(clean) != 6:
        raise ValueError(f"Invalid hex color code: '{hex_code}'")
    return int(clean[0:2], 16), int(clean[2:4], 16), int(clean[4:6], 16)


def hex_to_rgba(hex_code: str, opacity: float = 1.0) -> Tuple[int, int, int, int]:
    """Convert hex color and float opacity to (R, G, B, A) tuple in 0..255."""
    r, g, b = hex_to_rgb(hex_code)
    a = int(round(max(0.0, min(1.0, opacity)) * 255))
    return r, g, b, a


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert (R, G, B) in 0..255 to hex color string."""
    return f"#{r:02X}{g:02X}{b:02X}"


def interpolate_color(color1: str, color2: str, alpha: float) -> str:
    """Linearly interpolate between two hex colors by factor alpha in [0, 1]."""
    alpha = max(0.0, min(1.0, alpha))
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    r = int(round(r1 + (r2 - r1) * alpha))
    g = int(round(g1 + (g2 - g1) * alpha))
    b = int(round(b1 + (b2 - b1) * alpha))
    return rgb_to_hex(r, g, b)


def color_gradient(colors: List[str], length: int) -> List[str]:
    """Generate a discrete gradient of hex colors across a specified length."""
    if length <= 0:
        return []
    if length == 1:
        return [colors[0]]
    if len(colors) == 1:
        return [colors[0]] * length

    result: List[str] = []
    num_segments = len(colors) - 1
    for i in range(length):
        global_alpha = i / (length - 1)
        segment = min(int(global_alpha * num_segments), num_segments - 1)
        local_alpha = (global_alpha * num_segments) - segment
        result.append(interpolate_color(colors[segment], colors[segment + 1], local_alpha))
    return result
