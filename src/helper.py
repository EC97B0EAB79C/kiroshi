from PIL import Image, ImageDraw, ImageFont


def load_font(font_path, font_size):
    try:
        return ImageFont.truetype(font_path, font_size)
    except Exception:
        return ImageFont.load_default(size=font_size)


def position(bbox, width, height):
    content_width = bbox[2] - bbox[0]
    content_height = bbox[3] - bbox[1]
    x = (width - content_width) // 2
    y = (height - content_height) // 2
    return (x, y)


def cut_text(text, font, max_width):
    words = text.split()
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
