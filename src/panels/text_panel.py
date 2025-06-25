from PIL import Image, ImageDraw, ImageFont

from src.panel import Panel
import src.helper as Helper


class TextPanel(Panel):
    def __init__(self, width=800, height=480, settings={}, DEBUG=False):
        super().__init__(width, height, settings, DEBUG)

        # Text settings
        self.text = settings.get("text", "")
        self.font = settings.get("font")
        self.font_size = settings.get("font_size", 24)
        self.font_color = settings.get("font_color", "black")
        self.align = settings.get("align", "center")

        # Margin, padding and border settings
        self.padding = settings.get("padding", 10)

    def draw(self):
        image = super().draw()
        draw = ImageDraw.Draw(image)
        font = Helper.load_font(self.font, self.font_size)

        spacing = self.margin + self.padding

        draw_text = Helper.cut_text(self.text, font, self.width - spacing * 2)

        bbox = draw.textbbox((0, 0), draw_text, font=font, align=self.align)
        position = Helper.position(bbox, self.width, self.height, spacing)
        position = (
            position[0] - bbox[0],
            position[1] - bbox[1],
        )

        draw.text(
            position, draw_text, fill=self.font_color, font=font, align=self.align
        )

        if self.DEBUG:
            # Draw Bounding Box
            draw.rectangle(
                [
                    bbox[0] + position[0],
                    bbox[1] + position[1],
                    bbox[2] + position[0],
                    bbox[3] + position[1],
                ],
                outline="red",
                width=2,
            )
            # Draw content area
            draw.rectangle(
                [
                    (spacing, spacing),
                    (self.width - spacing, self.height - spacing),
                ],
                outline="blue",
                width=2,
            )

        return image
