from PIL import Image, ImageDraw, ImageFont


class Panel:
    def __init__(self, width=800, height=480, settings={}):
        self.width = width
        self.height = height
        self.settings = settings

        # Margin, padding and border settings
        self.margin = settings.get("margin", 10)
        self.border_color = settings.get("border_color", "black")
        self.border_width = settings.get("border_width", 2)

    def draw(self):
        image = Image.new("RGB", (self.width, self.height), "white")

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
