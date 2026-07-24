#!/usr/bin/env python3
"""Generate Hex.ico — a cyan hexagonal icon for HexLauncher.

Produces a multi-size .ico file (16, 32, 48, 64, 128, 256).
"""
import math
from PIL import Image, ImageDraw

# Cyberpunk cyan palette (matches main.py)
CYAN_BRIGHT = (0, 229, 255, 255)    # #00e5ff
CYAN_DARK   = (0, 131, 143, 255)    # #00838f
BG_DEEP     = (7, 9, 13, 255)       # #07090d


def hex_vertices(cx, cy, radius):
    return [
        (
            cx + radius * math.cos(math.radians(60 * i - 30)),
            cy + radius * math.sin(math.radians(60 * i - 30)),
        )
        for i in range(6)
    ]


def render(size: int) -> Image.Image:
    """Render the hexagonal icon at the given pixel size."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx = cy = size / 2
    r_outer = size * 0.45
    r_inner = size * 0.32

    # Dark rounded square background
    pad = size * 0.04
    draw.rounded_rectangle(
        (pad, pad, size - pad, size - pad),
        radius=size * 0.18,
        fill=BG_DEEP,
    )

    # Cyan outer hexagon
    draw.polygon(hex_vertices(cx, cy, r_outer), fill=CYAN_BRIGHT)

    # Darker inner hexagon for depth
    draw.polygon(hex_vertices(cx, cy, r_inner), fill=CYAN_DARK)

    return img


def main():
    # Render at max size and let PIL resize to smaller sizes for the .ico
    base = render(256)
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    base.save("Hex.ico", format="ICO", sizes=sizes)
    print(f"Written Hex.ico with sizes: {[s[0] for s in sizes]}")


if __name__ == "__main__":
    main()
