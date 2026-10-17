from datetime import datetime

from src.panels.text_panel import TextPanel


class TimePanel(TextPanel):
    """Text panel with date and time. Refreshes only when the minute changes."""

    def _draw(self, image):
        self.update_text(datetime.now().strftime("%Y-%m-%d\n%H:%M"))

        return super()._draw(image)
