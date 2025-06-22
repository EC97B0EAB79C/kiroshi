from PIL import Image, ImageDraw, ImageFont

from src.panel import Panel
import src.helper as helper


class TextPanel(Panel):
    def __init__(self, width=800, height=480, settings={}):
        super().__init__(width, height, settings)
        self.text = settings.get("text", "")
        self.font = settings.get("font")
        self.font_size = settings.get("font_size", 24)
        self.font_color = settings.get("font_color", "black")
        self.align = settings.get("align", "center")

    def draw(self):
        image = Image.new("RGB", (self.width, self.height), "white")
        draw = ImageDraw.Draw(image)
        font = helper.load_font(self.font, self.font_size)

        draw_text = helper.cut_text(self.text, font, self.width)

        bbox = draw.textbbox((0, 0), draw_text, font=font)
        position = helper.position(bbox, self.width, self.height)

        draw.text(
            position, draw_text, fill=self.font_color, font=font, align=self.align
        )

        return image
