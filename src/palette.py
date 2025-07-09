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
