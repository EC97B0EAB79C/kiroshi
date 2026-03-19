#!/usr/bin/python

import argparse
import sys
import signal
import logging

from src.app import Application

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

    # region: argument parsing
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
    # endregion

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        app_instance = Application(args.settings, args.debug)
        app_instance.run()
    except Exception as e:
        logger.error(f"Fatal error during execution: {e}")
        sys.exit(1)
    finally:
        logger.info("Application terminated.")


if __name__ == "__main__":
    main()
