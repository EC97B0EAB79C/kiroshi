from PIL import Image, ImageDraw, ImageFont


class Panel:
    def __init__(self, width=800, height=480, settings={}, Debug=False):
        self.width = width
        self.height = height
        self.settings = settings
        self.DEBUG = Debug

        # Margin, padding and border settings
        self.margin = settings.get("margin", 10)
        self.border_color = settings.get("border_color", "black")
        self.border_width = settings.get("border_width", 2)

        # Quantization settings
        self.palette_name = settings.get("palette", "6_colors")

    def draw(self):
        image = Image.new("RGB", (self.width, self.height), "white")
        image = self._draw(image)
        image = self._draw_border(image)
        if self.DEBUG:
            image = self._draw_debug(image)

        return image

    def _draw(self, image):
        return image

    def _draw_border(self, image):
        draw = ImageDraw.Draw(image)
        draw.rectangle(
            [
                (self.margin, self.margin),
                (self.width - self.margin, self.height - self.margin),
            ],
            outline=self.border_color,
            width=self.border_width,
        )

        return image

    def _draw_debug(self, image):
        draw = ImageDraw.Draw(image)
        draw.line(
            [(image.width // 2, 0), (image.width // 2, image.height)],
            fill="red",
            width=1,
        )
        draw.line(
            [(0, image.height // 2), (image.width, image.height // 2)],
            fill="red",
            width=1,
        )

        return image
