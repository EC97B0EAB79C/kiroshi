#!/usr/bin/python

import argparse
import os
import sys
import json
from time import sleep


from src.setting import Setting
from src.panels.loader import load_panel


DEBUG = False

USE_EPD = False
try:
    picdir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "pic"
    )
    libdir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "lib"
    )
    if os.path.exists(libdir):
        sys.path.append(libdir)

    from waveshare_epd import epd7in3e

    USE_EPD = True
except Exception as e:
    print(f"Error importing e-Paper library: {e}")
    USE_EPD = False


def set_panel(image):
    if USE_EPD:
        epd = epd7in3e.EPD()
        epd.init()
        epd.display(epd.getbuffer(image))
        epd.sleep()
    else:
        image.save("test_image.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Loader")
    parser.add_argument(
        "-s",
        "--settings",
        type=str,
        default="example/setting.json",
    )

    args = parser.parse_args()

    settings = Setting(args.settings)
    panels = {}

    while True:
        panel_id, current_panel_spec, duration = settings.get_next_panel()
        if panel_id not in panels:
            panels[panel_id] = load_panel(current_panel_spec)

        image = panels[panel_id].draw()

        set_panel(image)

        sleep(duration * 60)
