import logging
from datetime import datetime, timedelta
from typing import Awaitable, Callable, Optional

from PIL import Image, ImageDraw

import src.default as Default

logger = logging.getLogger(__name__)


class Panel:
    def __init__(self, width=800, height=480, settings=None, debug=False):
        settings = settings or {}
        self.width = width
        self.height = height
        self.settings = settings
        self.debug = debug

        # Margin, padding and border settings
        self.margin = settings.get("margin", Default.MARGIN)
        self.padding = settings.get("padding", Default.PADDING)
        self.border_color = settings.get("border_color", Default.BORDER_COLOR)
        self.border_width = settings.get("border_width", Default.BORDER_WIDTH)

        # Quantization settings
        self.palette_name = settings.get("palette", "6_colors")

        # Request settings (minutes between API requests)
        self.request_interval = settings.get("request_interval", 0)
        self.cache = None
        self.cache_time = datetime.min
        self.error = None

        # Refresh settings
        self.refresh = True

    def needs_refresh(self) -> bool:
        current, self.refresh = self.refresh, False
        return current

    def set_size(self, width, height):
        self.width = width
        self.height = height

    # Data panels set this to an async method that returns new data
    fetch: Optional[Callable[[], Awaitable]] = None

    async def update(self):
        """Get new data when it is due (once per request_interval).

        Set refresh when the data changes. On error, keep the last good data.
        """
        if self.fetch is None:
            return
        age = datetime.now() - self.cache_time
        if self.cache is not None and age < timedelta(minutes=self.request_interval):
            return

        try:
            data = await self.fetch()
        except Exception as e:
            logger.error(f"{type(self).__name__} request failed: {e}")
            if self.cache is None and self.error is None:
                self.refresh = True
            self.error = e
            return

        if data != self.cache or self.error is not None:
            self.refresh = True
        self.cache, self.cache_time, self.error = data, datetime.now(), None

    def draw(self) -> Image.Image:
        """Draw the panel from the data that update() got. No network here."""
        image = Image.new("RGB", (self.width, self.height), Default.BACKGROUND_COLOR)
        image = self._draw(image)
        image = self._draw_border(image)
        if self.debug:
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
