#!/usr/bin/python

import argparse
import os
import sys
import signal
import json
import logging
from time import sleep

from datetime import datetime, timezone, timedelta

from src.setting import Setting
from src.panels.loader import load_panel


DEBUG = False
USE_EPD = False
logger = None
epd = None


def signal_handler(sig, frame):
    global epd
    if USE_EPD and epd is not None:
        if logger:
            logger.info("Signal received, cleaning up e-Paper display")
        epd.init()
        epd.Clear()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def set_epd(name):
    global epd
    if not USE_EPD:
        return

    # Configure EPD library
    try:
        libdir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "lib"
        )
        if os.path.exists(libdir):
            sys.path.append(libdir)

        if name == "epd7in3e":
            from waveshare_epd import epd7in3e as epd_lib
        else:
            logger.warning(f"Unsupported e-Paper display: {name}")
            USE_EPD = False
            return

        epd = epd_lib.EPD()

        logger.info("e-Paper library imported successfully.")
        USE_EPD = True
        return
    except Exception as e:
        logger.warning(f"Error importing e-Paper library: {e}")
        USE_EPD = False


def set_panel(image, FULL_REFRESH=True):
    global epd
    if not USE_EPD or epd is None:
        logger.debug("e-Paper display not available, saving image to file")
        image.save("test_image.png")
        logger.debug("Image saved to test_image.png")

    if FULL_REFRESH:
        logger.debug("Displaying image on e-Paper display")
        epd.init()
        epd.display(epd.getbuffer(image))
        epd.sleep()
        logger.debug("Image displayed successfully on e-Paper display")
    else:
        logger.warning("Partial refresh not implemented")


def main(settings_file):
    logger.info(f"Starting application")
    settings = Setting(settings_file)
    set_epd(settings.get_epd_name())
    panels = {}

    last_update = datetime.min
    duration = 0
    while True:
        FULL_REFRESH = False
        if (datetime.now() - last_update).total_seconds() > duration * 60:
            panel_id, current_panel_spec, duration = settings.get_next_panel()
            logger.info(f"Displaying panel {panel_id} for {duration} minutes")
            last_update = datetime.now()
            FULL_REFRESH = True
            if current_panel_spec.get("refresh", False):
                refresh_interval = settings.get_refresh_interval()
            else:
                refresh_interval = duration * 60

        if panel_id not in panels:
            panels[panel_id] = load_panel(current_panel_spec, DEBUG=DEBUG)

        image = panels[panel_id].draw()
        set_panel(image, FULL_REFRESH=FULL_REFRESH)
        sleep(refresh_interval)


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Loader")
    parser.add_argument(
        "-s",
        "--settings",
        type=str,
        default="example/setting.json",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )
    args = parser.parse_args()
    DEBUG = args.debug

    # Set logger
    logging.basicConfig(
        level=logging.DEBUG if DEBUG else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger(__name__)

    # Main execution
    main(args.settings)
