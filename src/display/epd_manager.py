import os
import sys
import logging

logger = logging.getLogger(__name__)

class EPDManager:
    def __init__(self, display_name: str):
        self.epd = None
        self._initialize_epd(display_name)

    def _initialize_epd(self, name: str):
        libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib")
        logger.debug(f"Adding library directory to sys.path: {libdir}")

        if os.path.exists(libdir) and libdir not in sys.path:
            sys.path.append(libdir)

        # Configure EPD library
        try:
            if name == "epd7in3e":
                from waveshare_epd import epd7in3e as epd_lib
            else:
                logger.warning(f"Unsupported e-Paper display name: {name}")
                logger.warning("Using mock e-Paper display instead.")
                from waveshare_epd import mock as epd_lib

            epd = epd_lib.EPD()
            logger.info("e-Paper library imported successfully.")

        except Exception as e:
            logger.error(f"Error importing e-Paper library: {e}")
            raise RuntimeError("Failed to import e-Paper library")

    def set_panel(self, image, full_refresh: bool=True):
        if not full_refresh:
            logger.warning("Partial refresh not implemented")
            # TODO

        logger.debug("Displaying image on e-Paper display")
        self.epd.init()
        self.epd.display(epd.getbuffer(image))
        self.epd.sleep()
        logger.debug("Image displayed successfully on e-Paper display")

    def cleanup(self):
        if self.epd is not None:
            logger.info("Cleaning up e-Paper display")
            self.epd.init()
            self.epd.Clear()
