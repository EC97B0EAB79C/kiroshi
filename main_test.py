#!/usr/bin/python

import os


DEBUG = False


from src.panels.loader import load_panel

import sys
import os
import json

if __name__ == "__main__":
    PANEL_FILE_PATH = "example/four_panel.json"
    try:
        with open(PANEL_FILE_PATH, "r") as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading panel configuration from {PANEL_FILE_PATH}: {e}")
        sys.exit(1)

    panel = load_panel(config[0])
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
