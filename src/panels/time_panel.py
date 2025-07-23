from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

from src.panels.text_panel import TextPanel


class TimePanel(TextPanel):
    def __init__(self, width=800, height=480, settings={}, DEBUG=False):
        super().__init__(width, height, settings, DEBUG)

    def _draw(self, image):
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M")
        self.update_text(f"{current_date}\n{current_time}")

        return super()._draw(image)
