from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

from src.panels.text_panel import TextPanel


class TimePanel(TextPanel):
    def __inti__(self, width=800, height=480, settings={}, DEBUG=False):
        super().__init__(width, height, settings, DEBUG)

    def draw(self):
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M")
        self.text = f"{current_date}\n{current_time}"

        return super().draw()
