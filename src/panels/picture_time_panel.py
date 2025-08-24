
from src.panels.time_panel import TimePanel
from src.panels.picture_panel import PicturePanel


class PictureTimePanel(TimePanel):
    def __init__(self, width=800, height=480, settings={}, DEBUG=False):
        super().__init__(width, height, settings, DEBUG)
        self.picture_panel = PicturePanel(width, height, settings, DEBUG)

    def _draw(self, image):
        self.picture_panel._draw(image)
        return super()._draw(image)
