import sys
import logging
import importlib

import src.default as Default
from src.palette import EPD_PALETTE_MAP

logger = logging.getLogger(__name__)


class EPDManager:
    def __init__(self, display_name: str):
        libdir = str(Default.ROOT / "lib")
        if libdir not in sys.path:
            sys.path.append(libdir)

        if display_name not in EPD_PALETTE_MAP:
            logger.warning(f"Unsupported e-Paper display name: {display_name}")
            logger.warning("Using mock e-Paper display instead.")
            display_name = "mock"

        try:
            epd_lib = importlib.import_module(f"waveshare_epd.{display_name}")
            self.epd = epd_lib.EPD()
        except Exception as e:
            raise RuntimeError(f"Failed to import e-Paper library: {e}") from e

        self.palette = EPD_PALETTE_MAP[display_name]
        logger.info(f"e-Paper library {display_name} imported successfully.")

    def set_panel(self, image):
        logger.debug("Displaying image on e-Paper display")
        self.epd.init()
        self.epd.display(self.epd.getbuffer(image))
        self.epd.sleep()
        logger.debug("Image displayed successfully on e-Paper display")

    def cleanup(self):
        logger.info("Cleaning up e-Paper display")
        self.epd.init()
        self.epd.Clear()
        self.epd.sleep()
