from PIL import Image, ImageDraw, ImageFont

from src.panel import Panel
import src.helper as Helper


class PicturePanel(Panel):
    def __init__(self, width, height, settings=None, DEBUG=False):
        super().__init__(width, height, settings, DEBUG)
        self.picture = None

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
        picture = Helper.quantize_image(picture, self.palette_name)

        image.paste(picture, (self.margin, self.margin))
        return super()._draw(image)
