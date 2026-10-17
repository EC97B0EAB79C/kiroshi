from PIL import ImageDraw

from src.panel import Panel
import src.helper as Helper
import src.default as Default


class TextPanel(Panel):
    def __init__(self, width=800, height=480, settings=None, debug=False):
        super().__init__(width, height, settings, debug)
        settings = self.settings

        # Text settings
        self.font = settings.get("font", Default.FONT)
        self.font_size = settings.get("font_size", Default.FONT_SIZE["H2"])
        self.font_color = settings.get("font_color", Default.FONT_COLOR)
        self.align = settings.get("align", "center")
        self.location = settings.get("location", "center")
        self.outline_color = settings.get("outline_color", Default.OUTLINE_COLOR)
        self.outline_size = settings.get("outline_size", Default.OUTLINE_SIZE)

        # Initialize text and position
        self.text = None
        self.update_text(settings.get("text", ""))

    def set_size(self, width, height):
        super().set_size(width, height)
        self._update_text_size()

    def update_text(self, text):
        if text == self.text:
            return
        self.text = text
        self._update_text_size()
        self.refresh = True

    def _update_text_size(self):
        self.spacing = self.margin + self.padding

        font = Helper.load_font(self.font, self.font_size)
        self.draw_text = Helper.cut_text(self.text, font, self.width - self.spacing * 2)
        self.bbox = Helper.text_bbox(self.draw_text, font, self.align)
        x, y = Helper.position(
            self.bbox, self.width, self.height, self.spacing, location=self.location
        )
        self.position = (x - self.bbox[0], y - self.bbox[1])

    def _draw(self, image):
        draw = ImageDraw.Draw(image)
        font = Helper.load_font(self.font, self.font_size)
        text = {"text": self.draw_text, "font": font, "align": self.align}

        if self.outline_color:
            size = self.outline_size
            for dx, dy in [(-size, -size), (size, size), (-size, size), (size, -size)]:
                position = (self.position[0] + dx, self.position[1] + dy)
                draw.text(position, fill=self.outline_color, **text)

        draw.text(self.position, fill=self.font_color, **text)

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
