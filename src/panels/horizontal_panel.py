from PIL import Image, ImageDraw, ImageFont

from src.panel import Panel


class HorizontalPanel(Panel):
    def __init__(self, width=800, height=480, settings={}, DEBUG=False):
        super().__init__(width, height, settings, DEBUG)

        # Margin, padding and border settings
        self.padding = settings.get("padding", 10)

    def set_panels(self, panel1: Panel, panel2: Panel):
        self.panel1 = panel1
        self.panel2 = panel2

    def get_panel_size(self):
        spacing = self.margin + self.padding
        return (
            (self.width - self.margin * 2) // 2 - self.padding * 2,
            self.height - spacing * 2,
        )

    def draw(self):
        image = super().draw()
        draw = ImageDraw.Draw(image)

        spacing = self.margin + self.padding
        panel_width, panel_height = self.get_panel_size()

        panel1_image = self.panel1.draw()
        image.paste(panel1_image, (spacing, spacing))

        panel2_image = self.panel2.draw()
        image.paste(panel2_image, (self.width // 2 + self.padding, spacing))

        draw.line(
            [
                (self.width // 2, self.margin),
                (self.width // 2, self.height - self.margin),
            ],
            fill=self.border_color,
            width=self.border_width,
        )

        if self.DEBUG:
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

        return image
