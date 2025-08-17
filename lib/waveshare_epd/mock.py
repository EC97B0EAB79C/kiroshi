import logging

EPD_WIDTH = 800
EPD_HEIGHT = 480


logger = logging.getLogger(__name__)


class EPD:
    def __init__(self):
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        self.BLACK = 0x000000
        self.WHITE = 0xFFFFFF
        self.YELLOW = 0x00FFFF
        self.RED = 0x0000FF
        self.BLUE = 0xFF0000
        self.GREEN = 0x00FF00

    def init(self):
        logger.debug("Mock e-Paper display initialized")

    def display(self, image):
        logger.debug("e-Paper display not available, saving image to file")
        image.save("test_image.png")
        logger.debug("Image saved to test_image.png")

    def getbuffer(self, image):
        return image

    def sleep(self):
        logger.debug("Mock e-Paper display sleep")
