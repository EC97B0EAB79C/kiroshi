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


def main(settings_file):
    pass


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
