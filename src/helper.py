import json
import logging
import datetime
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import src.default as Default
from src.palette import PALETTE, PALETTE_6_COLORS

logger = logging.getLogger(__name__)


def resolve_path(file_path) -> Path:
    """Return an absolute path. A relative path starts at the project root."""
    path = Path(file_path)
    return path if path.is_absolute() else Default.ROOT / path


def load_json(file_path):
    try:
        with open(resolve_path(file_path), "r") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError) as e:
        raise ValueError(f"Cannot load JSON from {file_path}: {e}") from e


def get_file_modified_time(file_path) -> datetime.datetime:
    try:
        mod_timestamp = Path(resolve_path(file_path)).stat().st_mtime
        return datetime.datetime.fromtimestamp(mod_timestamp)
    except Exception as e:
        raise RuntimeError(f"Error getting modified time for {file_path}: {e}")


@lru_cache(maxsize=64)
def _load_font(font_path: str, font_size: int):
    try:
        return ImageFont.truetype(font_path, font_size)
    except Exception as e:
        logger.error(f"Error loading font '{font_path}': {e}")
        return ImageFont.load_default(size=font_size)


def load_font(font_path, font_size):
    return _load_font(str(resolve_path(font_path)), int(font_size))


def text_bbox(text, font, align="left"):
    return ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox(
        (0, 0), text, font=font, align=align
    )


def position(bbox, width, height, spacing=0, location="center"):
    content_width = bbox[2] - bbox[0]
    content_height = bbox[3] - bbox[1]
    x = ((width - spacing * 2) - content_width) // 2 + spacing
    y = ((height - spacing * 2) - content_height) // 2 + spacing
    if location == "top":
        y = spacing
    elif location == "bottom":
        y = height - content_height - spacing
    return (x, y)


def cut_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        if font.getbbox(test_line)[2] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return "\n".join(lines)


def truncate_text(text, font, max_width):
    if font.getbbox(text)[2] <= max_width:
        return text

    ellipsis = "..."
    while font.getbbox(text + ellipsis)[2] > max_width:
        if not text:
            return ""
        text = text[:-1]
    return text + ellipsis


def fit_and_crop_picture(picture, target_size):
    pic_width, pic_height = picture.size
    target_width, target_height = target_size

    scale = max(target_width / pic_width, target_height / pic_height)

    new_width = int(pic_width * scale)
    new_height = int(pic_height * scale)
    resized_picture = picture.resize((new_width, new_height), Image.Resampling.LANCZOS)

    if new_width > target_width or new_height > target_height:
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        resized_picture = resized_picture.crop(
            (left, top, left + target_width, top + target_height)
        )

    return resized_picture


def quantize_image(image, palette):
    palette_colors = PALETTE.get(palette, PALETTE_6_COLORS)
    palette_image = Image.new("P", (1, 1))
    palette_image.putpalette(palette_colors)
    return image.quantize(palette=palette_image, dither=Image.Dither.FLOYDSTEINBERG)


def error_text(title, error):
    """Short error text for the display, for example 'GitHub error\\nHTTPError 401'."""
    status = getattr(getattr(error, "response", None), "status_code", None)
    detail = f"{type(error).__name__} {status or ''}".strip()
    return f"{title}\n{detail}"


def invalid_image(image, width, height, text="Invalid API Response", spacing=10):
    draw = ImageDraw.Draw(image)
    font_size = 48
    while font_size > 0:
        font = load_font(Default.FONT, font_size)
        text_size = draw.textbbox((0, 0), text, font=font)
        if (text_size[2] - text_size[0]) <= (width - spacing * 2) and (
            text_size[3] - text_size[1]
        ) <= (height - spacing * 2):
            break
        font_size -= 1

    text_size = draw.textbbox((0, 0), text, font=font)

    try:
        error_icon = Image.open(resolve_path(Default.ERROR_ICON)).convert("RGBA")
        transparent_bg = Image.new("RGBA", error_icon.size, (255, 255, 255, 0))
        error_icon = Image.alpha_composite(transparent_bg, error_icon)

        distance = 20
        combined_height = error_icon.height + distance + text_size[3]
        start_y = (height - combined_height) // 2
        image.paste(error_icon, ((width - error_icon.width) // 2, start_y))

        text_x = (width - text_size[2]) // 2
        text_y = start_y + error_icon.height + distance

    except Exception as e:
        logger.error(f"Error loading icon: {e}")
        text_x = (width - text_size[2]) // 2
        text_y = (height - text_size[3]) // 2

    if font_size > 0:
        draw.text((text_x, text_y), text, fill="black", font=font, align="center")

    return image
