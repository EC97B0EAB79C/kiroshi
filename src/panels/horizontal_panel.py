from PIL import Image, ImageDraw, ImageFont

from src.panel import Panel


class HorizontalPanel(Panel):
    def __init__(
        self,
        width=800,
        height=480,
        settings={},
        DEBUG=False,
        /,
        panel1=None,
        panel2=None,
    ):
        super().__init__(width, height, settings, DEBUG)

        # Margin, padding and border settings
        self.padding = settings.get("padding", 10)

        self.set_panels(panel1, panel2)

    def set_panels(self, /, panel1: Panel = None, panel2: Panel = None):
        if isinstance(panel1, Panel):
            self.panel1 = panel1
        if isinstance(panel2, Panel):
            self.panel2 = panel2

        self._set_panel_size()

    def get_panel_size(self):
        spacing = self.margin + self.padding
        return (
            (self.width - self.margin * 2) // 2 - self.padding * 2,
            self.height - spacing * 2,
        )

    def _set_panel_size(self):
        target_width, target_height = self.get_panel_size()
        if isinstance(self.panel1, Panel):
            self.panel1.set_size(target_width, target_height)
        if isinstance(self.panel2, Panel):
            self.panel2.set_size(target_width, target_height)

    def _draw(self, image):
        spacing = self.margin + self.padding

        if isinstance(self.panel1, Panel):
            panel1_image = self.panel1.draw()
            image.paste(panel1_image, (spacing, spacing))

        if isinstance(self.panel2, Panel):
            panel2_image = self.panel2.draw()
            image.paste(panel2_image, (self.width // 2 + self.padding, spacing))

        return super()._draw(image)

    def _draw_border(self, image):
        draw = ImageDraw.Draw(image)

        draw.line(
            [
                (self.width // 2, self.margin),
                (self.width // 2, self.height - self.margin),
            ],
            fill=self.border_color,
            width=self.border_width,
        )

        return super()._draw_border(image)

    def _draw_debug(self, image):
        draw = ImageDraw.Draw(image)

        spacing = self.margin + self.padding
        panel_width, panel_height = self.get_panel_size()

        draw.rectangle(
            [
                (spacing, spacing),
                (spacing + panel_width, spacing + panel_height),
            ],
            outline="blue",
            width=2,
        )

        draw.rectangle(
            [
                (self.width // 2 + self.padding, spacing),
                (
                    self.width // 2 + self.padding + panel_width,
                    spacing + panel_height,
                ),
            ],
            outline="blue",
            width=2,
        )

        return super()._draw_debug(image)
