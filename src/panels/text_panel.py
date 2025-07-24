from PIL import Image, ImageDraw, ImageFont

from src.panel import Panel
import src.helper as Helper


class TextPanel(Panel):
    def __init__(self, width=800, height=480, settings={}, DEBUG=False):
        super().__init__(width, height, settings, DEBUG)

        # Text settings
        self.font = settings.get("font")
        self.font_size = settings.get("font_size", 24)
        self.font_color = settings.get("font_color", "black")
        self.align = settings.get("align", "center")

        # Margin, padding and border settings
        self.padding = settings.get("padding", 10)

        # Initialize text and position
        self.update_text(settings.get("text", ""))

    def set_size(self, width, height):
        super().set_size(width, height)
        self._update_text_size()

    def update_text(self, text):
        self.text = text
        self._update_text_size()

    def _update_text_size(self):
        self.spacing = self.margin + self.padding

        font = Helper.load_font(self.font, self.font_size)
        self.draw_text = Helper.cut_text(self.text, font, self.width - self.spacing * 2)
        self.bbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox(
            (0, 0), self.draw_text, font=font, align=self.align
        )
        self.position = Helper.position(
            self.bbox, self.width, self.height, self.spacing
        )
        self.position = (
            self.position[0] - self.bbox[0],
            self.position[1] - self.bbox[1],
        )

    def _draw(self, image):
        draw = ImageDraw.Draw(image)
        font = Helper.load_font(self.font, self.font_size)

        draw.text(
            self.position,
            self.draw_text,
            fill=self.font_color,
            font=font,
            align=self.align,
        )

        return super()._draw(image)

    def _draw_debug(self, image):
        draw = ImageDraw.Draw(image)
        draw.rectangle(
            [
                self.bbox[0] + self.position[0],
                self.bbox[1] + self.position[1],
                self.bbox[2] + self.position[0],
                self.bbox[3] + self.position[1],
            ],
            outline="red",
            width=2,
        )
        # Draw content area
        draw.rectangle(
            [
                (self.spacing, self.spacing),
                (self.width - self.spacing, self.height - self.spacing),
            ],
            outline="blue",
            width=2,
        )
        return super()._draw_debug(image)
