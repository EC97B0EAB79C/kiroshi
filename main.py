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
logger = None
epd = None


def signal_handler(sig, frame):
    global epd
    if epd is not None:
        if logger:
            logger.info("Signal received, cleaning up e-Paper display")
        epd.init()
        epd.Clear()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def set_epd(name):
    global epd, logger

    # Configure EPD library
    try:
        libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib")
        logger.debug(f"Adding library directory to sys.path: {libdir}")
        if os.path.exists(libdir):
            sys.path.append(libdir)

        if name == "epd7in3e":
            from waveshare_epd import epd7in3e as epd_lib
        else:
            logger.warning(f"Unsupported e-Paper display name: {name}")
            logger.warning("Using mock e-Paper display instead.")
            from waveshare_epd import mock as epd_lib

        epd = epd_lib.EPD()

        logger.info("e-Paper library imported successfully.")
        return
    except Exception as e:
        logger.error(f"Error importing e-Paper library: {e}")
        raise RuntimeError("Failed to import e-Paper library")


def set_panel(image, FULL_REFRESH=True):
    global epd

    if not FULL_REFRESH:
        logger.warning("Partial refresh not implemented")
        # TODO
        # return

    logger.debug("Displaying image on e-Paper display")
    epd.init()
    epd.display(epd.getbuffer(image))
    epd.sleep()
    logger.debug("Image displayed successfully on e-Paper display")


def main(settings_file):
    global epd
    logger.info(f"Starting application")
    settings = Setting(settings_file)
    set_epd(settings.get_epd_name())
    settings.set_epd_settings(epd)
    panels = {}

    last_update = datetime.min
    duration = 0
    while True:
        FULL_REFRESH = False
        if (datetime.now() - last_update).total_seconds() > duration:
            panel_id, current_panel_spec, duration = settings.get_next_panel()
            logger.info(f"Displaying panel {panel_id} for {duration} seconds")
            last_update = datetime.now()
            FULL_REFRESH = True
            if current_panel_spec.get("refresh", False):
                refresh_interval = settings.get_refresh_interval()
            else:
                refresh_interval = duration

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
