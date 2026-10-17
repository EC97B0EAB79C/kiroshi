import logging

from PIL import Image

from src.panel import Panel
import src.helper as Helper


logger = logging.getLogger(__name__)


class PicturePanel(Panel):
    def __init__(self, width, height, settings=None, debug=False):
        super().__init__(width, height, settings, debug)
        self.picture = None
        self.processed = None
        if "picture" in self.settings:
            self.set_picture(self.settings["picture"])

    def set_picture(self, picture_path):
        try:
            self.picture = Image.open(Helper.resolve_path(picture_path)).convert("RGB")
        except Exception as e:
            logger.error(f"Error loading picture: {e}")

        self.processed = None
        self.refresh = True

    def _draw(self, image):
        if not self.picture:
            logger.warning("Picture not set.")
            return super()._draw(image)

        # Resize and quantize only when the size or the picture changes
        size = (self.width - 2 * self.margin, self.height - 2 * self.margin)
        if self.processed is None or self.processed.size != size:
            picture = Helper.fit_and_crop_picture(self.picture, size)
            self.processed = Helper.quantize_image(picture, self.palette_name)

        image.paste(self.processed, (self.margin, self.margin))
        return super()._draw(image)
