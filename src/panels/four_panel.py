from PIL import Image, ImageDraw, ImageFont

from src.panel import Panel


class FourPanel(Panel):
    def __init__(
        self,
        width=800,
        height=480,
        settings={},
        DEBUG=False,
        panel1=None,
        panel2=None,
        panel3=None,
        panel4=None,
    ):
        super().__init__(width, height, settings, DEBUG)

        # Margin, padding and border settings
        self.padding = settings.get("padding", 10)

        self.set_panels(panel1, panel2, panel3, panel4)

    def set_panels(
        self,
        panel1: Panel = None,
        panel2: Panel = None,
        panel3: Panel = None,
        panel4: Panel = None,
    ):
        if isinstance(panel1, Panel):
            self.panel1 = panel1
        if isinstance(panel2, Panel):
            self.panel2 = panel2
        if isinstance(panel3, Panel):
            self.panel3 = panel3
        if isinstance(panel4, Panel):
            self.panel4 = panel4

        self._set_panel_size()

    def set_size(self, width, height):
        super().set_size(width, height)
        self._set_panel_size()

    def get_panel_size(self):
        return (
            (self.width - self.margin * 2) // 2 - self.padding * 2,
            (self.height - self.margin * 2) // 2 - self.padding * 2,
        )

    def _set_panel_size(self):
        target_width, target_height = self.get_panel_size()
        if isinstance(self.panel1, Panel):
            self.panel1.set_size(target_width, target_height)
        if isinstance(self.panel2, Panel):
            self.panel2.set_size(target_width, target_height)
        if isinstance(self.panel3, Panel):
            self.panel3.set_size(target_width, target_height)
        if isinstance(self.panel4, Panel):
            self.panel4.set_size(target_width, target_height)

    def _draw(self, image):
        spacing = self.margin + self.padding

        if isinstance(self.panel1, Panel):
            panel1_image = self.panel1.draw()
            image.paste(panel1_image, (spacing, spacing))

        if isinstance(self.panel2, Panel):
            panel2_image = self.panel2.draw()
            image.paste(panel2_image, (self.width // 2 + self.padding, spacing))

        if isinstance(self.panel3, Panel):
            panel3_image = self.panel3.draw()
            image.paste(panel3_image, (spacing, self.height // 2 + self.padding))

        if isinstance(self.panel4, Panel):
            panel4_image = self.panel4.draw()
            image.paste(
                panel4_image,
                (self.width // 2 + self.padding, self.height // 2 + self.padding),
            )

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

        draw.line(
            [
                (self.margin, self.height // 2),
                (self.width - self.margin, self.height // 2),
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

        draw.rectangle(
            [
                (spacing, self.height // 2 + self.padding),
                (
                    spacing + panel_width,
                    self.height // 2 + self.padding + panel_height,
                ),
            ],
            outline="blue",
            width=2,
        )

        draw.rectangle(
            [
                (self.width // 2 + self.padding, self.height // 2 + self.padding),
                (
                    self.width // 2 + self.padding + panel_width,
                    self.height // 2 + self.padding + panel_height,
                ),
            ],
            outline="blue",
            width=2,
        )

        return super()._draw_debug(image)
