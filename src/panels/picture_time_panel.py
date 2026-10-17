from src.panels.time_panel import TimePanel
from src.panels.picture_panel import PicturePanel


class PictureTimePanel(TimePanel):
    def __init__(self, width=800, height=480, settings=None, debug=False):
        super().__init__(width, height, settings, debug)
        self.picture_panel = PicturePanel(width, height, self.settings, debug)

    def needs_refresh(self) -> bool:
        picture = self.picture_panel.needs_refresh()
        return super().needs_refresh() or picture

    def set_size(self, width, height):
        super().set_size(width, height)
        self.picture_panel.set_size(width, height)

    def _draw(self, image):
        self.picture_panel._draw(image)
        return super()._draw(image)
