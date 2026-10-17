#!/usr/bin/python

import os
import sys
import signal
import logging
import argparse

import src.helper as Helper
from src.app import Application
from src.display.epd_manager import EPDManager

logger = logging.getLogger(__name__)
app_instance = None


def signal_handler(sig, frame):
    logger.info("Signal received, initiating graceful shutdown...")
    if app_instance is not None:
        app_instance.stop()
    else:
        sys.exit(0)


def main():
    global app_instance

    parser = argparse.ArgumentParser(description="Kiroshi e-Paper dashboard")
    parser.add_argument("-s", "--settings", type=str, default="example/setting.json")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--once", action="store_true", help="Draw the next panel one time and exit")
    parser.add_argument("--clear", action="store_true", help="Clear the display and exit")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # The settings path is relative to the current directory
    settings_file = os.path.abspath(args.settings)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        if args.clear:
            EPDManager(Helper.load_json(settings_file).get("epd", "mock")).cleanup()
            return

        app_instance = Application(settings_file, args.debug)
        if args.once:
            app_instance.draw_once()
        else:
            app_instance.run()
    except Exception as e:
        logger.error(f"Fatal error during execution: {e}")
        sys.exit(1)
    finally:
        logger.info("Application terminated.")


if __name__ == "__main__":
    main()
