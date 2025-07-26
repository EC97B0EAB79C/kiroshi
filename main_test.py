#!/usr/bin/python

import os

from PIL import Image, ImageDraw, ImageFont

from src.panel import Panel
from src.panels.text_panel import TextPanel
from src.panels.time_panel import TimePanel
from src.panels.horizontal_panel import HorizontalPanel
from src.panels.vertical_panel import VerticalPanel
from src.panels.four_panel import FourPanel
from src.panels.picture_panel import PicturePanel
from src.panels.toggl_panel import TogglPanel
from src.panels.calendar_panel import CalendarPanel
from src.panels.github_panel import GithubPanel

DEBUG = False
TEST_FONT = "fonts/roboto_mono/static/RobotoMono-Regular.ttf"


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
