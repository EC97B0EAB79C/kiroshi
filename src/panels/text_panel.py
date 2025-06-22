from PIL import Image, ImageDraw, ImageFont

from src.panel import Panel


class TextPanel(Panel):
    def __init__(self, width=800, height=480, settings={}):
        super().__init__(width, height, settings)
        self.text = settings.get("text", "")
        self.font = settings.get("font")
        self.font_size = settings.get("font_size", 24)
        self.font_color = settings.get("font_color", "black")

    def draw(self):
        image = Image.new("RGB", (self.width, self.height), "white")
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype(self.font, self.font_size)

        except Exception:
            font = ImageFont.load_default(size=self.font_size)

        bbox = draw.textbbox((0, 0), self.text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((self.width - text_width) // 2, (self.height - text_height) // 2)

        draw.text(position, self.text, fill=self.font_color, font=font)

        return image
