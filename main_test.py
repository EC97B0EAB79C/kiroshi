#!/usr/bin/python

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

DEBUG = False
TEST_FONT = "fonts/roboto_mono/static/RobotoMono-Regular.ttf"


def test_picture_panel():
    # picture = "../pic/Cyberpunk2077_Wallpapers_TraumaTeam_3840x2160_EN.png"
    picture = "../pic/kv_pc.jpg"

    panel = PicturePanel(
        width=800,
        height=480,
        settings={},
        DEBUG=DEBUG,
    )
    panel.set_picture(picture)
    image = panel.draw()

    return image


def test_four_panel():
    panel = FourPanel(
        width=800,
        height=480,
        settings={
            "padding": 0,
        },
        DEBUG=DEBUG,
    )
    size = panel.get_panel_size()

    text_panel = TextPanel(
        width=size[0],
        height=size[1],
        settings={
            "text": "Text Panel",
            "font": TEST_FONT,
            "font_size": 24,
            "font_color": "black",
            "align": "center",
            "margin": 10,
            "border_width": 0,
            "padding": 10,
        },
        DEBUG=DEBUG,
    )

    time_panel = TimePanel(
        width=size[0],
        height=size[1],
        settings={
            "font": TEST_FONT,
            "font_size": 24,
            "font_color": "black",
            "align": "center",
            "margin": 10,
            "padding": 10,
        },
        DEBUG=DEBUG,
    )

    toggl_panel = TogglPanel(
        width=size[0],
        height=size[1],
        settings={
            "api_key": "",
            "margin": 0,
            "padding": 10,
            "border_color": "black",
            "border_width": 0,
            "font": "fonts/noto_sans_with_emoji/NotoSansWithEmoji-Scaled.ttf",
        },
        DEBUG=DEBUG,
    )

    panel.set_panels(text_panel, time_panel, toggl_panel, time_panel)
    image = panel.draw()

    return image


def test_calendar_panel():

    panel = CalendarPanel(
        width=800,
        height=480,
        settings={
            "ical_urls": [
                "https://calendar.google.com/calendar/ical/en.japanese%23holiday%40group.v.calendar.google.com/public/basic.ics",
                "https://calendar.google.com/calendar/ical/en.south_korea%23holiday%40group.v.calendar.google.com/public/basic.ics",
            ],
            "font": TEST_FONT,
            "font_size": 24,
            "font_color": "black",
            "padding": 10,
        },
        DEBUG=DEBUG,
    )
    image = panel.draw()

    return image


import sys
import os

picdir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "pic"
)
libdir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "lib"
)
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd7in3e

if __name__ == "__main__":
    # image = test_four_panel()
    # image = test_picture_panel()
    image = test_calendar_panel()

    epd = epd7in3e.EPD()
    epd.init()
    epd.Clear()

    # Display the image on the e-Paper
    epd.display(epd.getbuffer(image))
    epd.sleep()
