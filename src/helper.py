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
