from PIL import Image, ImageDraw, ImageFont

from src.panel import Panel
import src.helper as Helper

palette_colors = [
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


class PicturePanel(Panel):
    def __init__(self, width, height, settings=None, DEBUG=False):
        super().__init__(width, height, settings, DEBUG)
        self.picture = None

    def set_picture(self, picture_path):
        self.picture = Image.open(picture_path).convert("RGB")

    def draw(self):
        if not self.picture:
            raise ValueError("Picture not set. Use set_picture() to set a picture.")

        image = super().draw()
        draw = ImageDraw.Draw(image)

        content_size = (
            self.width - 2 * self.margin,
            self.height - 2 * self.margin,
        )

        picture = Helper.fit_and_crop_picture(self.picture, content_size)
        palette_colors.extend([0] * (256 - len(palette_colors)))
        palette_image = Image.new("P", (1, 1))
        palette_image.putpalette(palette_colors)
        palette_image = picture.quantize(
            palette=palette_image, dither=Image.Dither.FLOYDSTEINBERG
        )

        image.paste(palette_image, (self.margin, self.margin))
        return image
