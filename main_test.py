#!/usr/bin/python

import sys
import os
import json

from src.setting import Setting
from src.panels.loader import load_panel


DEBUG = False


if __name__ == "__main__":
    PANEL_FILE_PATH = "example/setting.json"
    settings = Setting(PANEL_FILE_PATH)

    _, current_panel_spec, duration = settings.get_next_panel()

    panel = load_panel(current_panel_spec)
    image = panel.draw()

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

        epd = epd7in3e.EPD()
        epd.init()
        # epd.Clear()

        # Display the image on the e-Paper
        epd.display(epd.getbuffer(image))
        epd.sleep()
    except Exception as e:
        print(f"Error displaying image on e-Paper: {e}")
        image.save("test_image.png")
