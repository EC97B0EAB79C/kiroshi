from PIL import Image, ImageDraw, ImageFont

from src.panel import Panel
import src.helper as Helper
from src.palette import *


class PicturePanel(Panel):
    def __init__(self, width, height, settings=None, DEBUG=False):
        super().__init__(width, height, settings, DEBUG)
        self.picture = None

        self.palette_name = settings.get("palette", "6_colors")

    def set_picture(self, picture_path):
        self.picture = Image.open(picture_path).convert("RGB")

    def _draw(self, image):
        if not self.picture:
            raise ValueError("Picture not set. Use set_picture() to set a picture.")

        draw = ImageDraw.Draw(image)

        content_size = (
            self.width - 2 * self.margin,
            self.height - 2 * self.margin,
        )

        picture = Helper.fit_and_crop_picture(self.picture, content_size)
        palette_colors = PALETTE.get(self.palette_name, PALETTE_6_COLORS)
        palette_colors.extend([0] * (256 - len(palette_colors)))
        palette_image = Image.new("P", (1, 1))
        palette_image.putpalette(palette_colors)
        palette_image = picture.quantize(
            palette=palette_image, dither=Image.Dither.FLOYDSTEINBERG
        )

        image.paste(palette_image, (self.margin, self.margin))
        return image
