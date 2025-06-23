from PIL import Image


class Panel:
    def __init__(self, width=800, height=480, settings={}):
        self.width = width
        self.height = height
        self.settings = settings
        self.padding = settings.get("padding", 10)

    def draw(self):
        image = Image.new("RGB", (self.width, self.height), "white")

        return image
