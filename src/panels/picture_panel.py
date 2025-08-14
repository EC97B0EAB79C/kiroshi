import logging
from PIL import Image, ImageDraw, ImageFont

from src.panel import Panel
import src.helper as Helper


logger = logging.getLogger(__name__)


class PicturePanel(Panel):
    def __init__(self, width, height, settings=None, DEBUG=False):
        super().__init__(width, height, settings, DEBUG)
        if settings and "picture" in settings:
            self.set_picture(settings["picture"])
        else:
            self.picture = None

    def set_picture(self, picture_path):
        try:
            self.picture = Image.open(picture_path).convert("RGB")
        except Exception as e:
            logger.error(f"Error loading picture: {e}")

    def _draw(self, image):
        if not self.picture:
            logger.warning("Picture not set.")
            return super()._draw(image)

        draw = ImageDraw.Draw(image)

        content_size = (
            self.width - 2 * self.margin,
            self.height - 2 * self.margin,
        )

        picture = Helper.fit_and_crop_picture(self.picture, content_size)
        picture = Helper.quantize_image(picture, self.palette_name)

        image.paste(picture, (self.margin, self.margin))
        return super()._draw(image)
