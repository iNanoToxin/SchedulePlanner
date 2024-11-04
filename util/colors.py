from matplotlib.colors import to_rgb, XKCD_COLORS
from typing import List
import random

def get_dark_mode_colors() -> List[str]:
    """Generates a list of suitable colors for dark mode from XKCD colors."""
    dark_mode_colors = []

    for color in XKCD_COLORS.values():
        r, g, b = to_rgb(color)
        luminance = (r * 0.299 + g * 0.587 + b * 0.114) * 255

        if 50 <= luminance <= 80:
            dark_mode_colors.append(color)

    dark_mode_colors.sort()
    random.seed(2025)
    random.shuffle(dark_mode_colors)
    return dark_mode_colors
