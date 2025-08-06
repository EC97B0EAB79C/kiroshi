import json

from PIL import Image, ImageDraw, ImageFont
from src.palette import *


def load_json(file_path):
    try:
        with open(file_path, "r") as file:
            content = json.load(file)
            return content
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}")
        return {}
    except Exception as e:
        print(f"Unexpected error loading JSON from {file_path}: {e}")
        return {}


def load_font(font_path, font_size):
    font_size = int(font_size)
    try:
        return ImageFont.truetype(font_path, font_size)
    except Exception as e:
        print(f"Error loading font '{font_path}': {e}")
        return ImageFont.load_default(size=font_size)


def position(bbox, width, height, spacing=0):
    content_width = bbox[2] - bbox[0]
    content_height = bbox[3] - bbox[1]
    x = ((width - spacing * 2) - content_width) // 2 + spacing
    y = ((height - spacing * 2) - content_height) // 2 + spacing
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

    scale_width = target_width / pic_width
    scale_height = target_height / pic_height
    scale = max(scale_width, scale_height)

    new_width = int(pic_width * scale)
    new_height = int(pic_height * scale)
    resized_picture = picture.resize((new_width, new_height), Image.Resampling.LANCZOS)

    if new_width > target_width or new_height > target_height:
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        resized_picture = resized_picture.crop((left, top, right, bottom))

    return resized_picture


def quantize_image(image, palette):
    palette_colors = PALETTE.get(palette, PALETTE_6_COLORS)
    palette_image = Image.new("P", (1, 1))
    palette_image.putpalette(palette_colors)
    return image.quantize(palette=palette_image, dither=Image.Dither.FLOYDSTEINBERG)


def invalid_image(image, width, height, text="Invalid API Response", spacing=10):
    draw = ImageDraw.Draw(image)
    font_size = 48
    while font_size > 0:
        font = load_font("fonts/roboto_mono/static/RobotoMono-Regular.ttf", font_size)
        text_size = draw.textbbox((0, 0), text, font=font)
        if (text_size[2] - text_size[0]) <= (width - spacing * 2) and (
            text_size[3] - text_size[1]
        ) <= (height - spacing * 2):
            break
        font_size -= 1

    text_size = draw.textbbox((0, 0), text, font=font)

    try:
        icon_path = "icons/error_72dp.png"
        error_icon = Image.open(icon_path).convert("RGBA")
        transparent_bg = Image.new("RGBA", error_icon.size, (255, 255, 255, 0))
        error_icon = Image.alpha_composite(transparent_bg, error_icon)

        distance = 20
        combined_height = error_icon.height + distance + text_size[3]
        start_y = (height - combined_height) // 2
        icon_x = (width - error_icon.width) // 2
        icon_y = start_y
        image.paste(error_icon, (icon_x, icon_y))

        text_x = (width - text_size[2]) // 2
        text_y = start_y + error_icon.height + distance

    except Exception as e:
        print(f"Error loading icon: {e}")
        text_x = (width - text_size[2]) // 2
        text_y = (height - text_size[3]) // 2

    if font_size > 0:
        draw.text((text_x, text_y), text, fill="black", font=font, align="center")

    return image
