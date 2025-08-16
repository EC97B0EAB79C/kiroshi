EPD_PALETTE_MAP = {
    "epd7in3e": "6_colors",
}


PALETTE_RED = 0x0000FF
PALETTE_GREEN = 0x00FF00
PALETTE_BLUE = 0xFF0000
PALETTE_YELLOW = 0x00FFFF
PALETTE_BLACK = 0x000000
PALETTE_WHITE = 0xFFFFFF

PALETTE_6_COLORS = [
    0,
    0,
    0,  # Black
    255,
    255,
    255,  # White
    255,
    0,
    0,  # Red
    0,
    255,
    0,  # Green
    0,
    0,
    255,  # Blue
    255,
    255,
    0,  # Yellow
]
PALETTE_6_COLORS.extend([0] * (256 - len(PALETTE_6_COLORS)))
PALETTE_6_COLOR_NAMES = [
    "black",
    "white",
    "red",
    "green",
    "blue",
    "yellow",
]
PALETTE_GRAY_COLORS = [
    0,
    0,
    0,
    85,
    85,
    85,
    127,
    127,
    127,
    191,
    191,
    191,
    255,
    255,
    255,
]
PALETTE_GRAY_COLORS.extend([0] * (256 - len(PALETTE_GRAY_COLORS)))
PALETTE = {
    "6_colors": PALETTE_6_COLORS,
    "gray": PALETTE_GRAY_COLORS,
}
