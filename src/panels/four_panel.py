from PIL import Image, ImageDraw, ImageFont

from src.panel import Panel


class FourPanel(Panel):
    def __init__(self, width=800, height=480, settings={}):
        super().__init__(width, height, settings)
        self.border_color = settings.get("border_color", "black")
        self.border_width = settings.get("border_width", 2)

    def set_panels(self, panel1: Panel, panel2: Panel, panel3: Panel, panel4: Panel):
        self.panel1 = panel1
        self.panel2 = panel2
        self.panel3 = panel3
        self.panel4 = panel4

    def get_panel_size(self):
        return (
            (self.width - self.padding * 2) // 2,
            (self.height - self.padding * 2) // 2,
        )

    def draw(self):
        image = Image.new("RGB", (self.width, self.height), "white")
        draw = ImageDraw.Draw(image)

        panel_width, panel_height = self.get_panel_size()

        panel1_image = self.panel1.draw()
        image.paste(panel1_image, (self.padding, self.padding))

        panel2_image = self.panel2.draw()
        image.paste(panel2_image, (self.padding + panel_width, self.padding))

        panel3_image = self.panel3.draw()
        image.paste(panel3_image, (self.padding, self.padding + panel_height))

        panel4_image = self.panel4.draw()
        image.paste(
            panel4_image, (self.padding + panel_width, self.padding + panel_height)
        )

        draw.rectangle(
            [
                (self.padding, self.padding),
                (self.width - self.padding, self.height - self.padding),
            ],
            outline=self.border_color,
            width=self.border_width,
        )
        draw.line(
            [
                (self.padding + panel_width, self.padding),
                (self.padding + panel_width, self.height - self.padding),
            ],
            fill=self.border_color,
            width=self.border_width,
        )
        draw.line(
            [
                (self.padding, self.padding + panel_height),
                (self.width - self.padding, self.padding + panel_height),
            ],
            fill=self.border_color,
            width=self.border_width,
        )

        return image
