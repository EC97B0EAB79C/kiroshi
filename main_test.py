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
TOGGL_API_KEY = os.getenv("TOGGL_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def get_picture_panel(size=(800, 480)):
    # picture = "../pic/Cyberpunk2077_Wallpapers_TraumaTeam_3840x2160_EN.png"
    picture = "../pic/kv_pc.jpg"

    panel = PicturePanel(
        width=size[0],
        height=size[1],
        settings={},
        DEBUG=DEBUG,
    )
    panel.set_picture(picture)
    return panel


def get_time_panel(size=(800, 480)):
    return TimePanel(
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


def get_text_panel(size=(800, 480)):
    text = "The quick brown fox jumps over the lazy dog."

    return TextPanel(
        width=size[0],
        height=size[1],
        settings={
            "text": text,
            "font": TEST_FONT,
            "font_size": 24,
            "font_color": "black",
            "align": "center",
            "margin": 10,
            "padding": 10,
        },
        DEBUG=DEBUG,
    )


def get_toggl_panel(size=(800, 480)):
    return TogglPanel(
        width=size[0],
        height=size[1],
        settings={
            "api_key": TOGGL_API_KEY,
            "margin": 0,
            "padding": 10,
            "border_color": "black",
            "border_width": 0,
            "font": "fonts/noto_sans_with_emoji/NotoSansWithEmoji-Scaled.ttf",
        },
        DEBUG=DEBUG,
    )


def get_calendar_panel(size=(800, 480)):
    return CalendarPanel(
        width=size[0],
        height=size[1],
        settings={
            "ical_urls": [
                "https://calendar.google.com/calendar/ical/en.japanese%23holiday%40group.v.calendar.google.com/public/basic.ics",
                "https://calendar.google.com/calendar/ical/en.south_korea%23holiday%40group.v.calendar.google.com/public/basic.ics",
            ],
            "font": TEST_FONT,
            "font_size": 24,
            "font_color": "black",
            "border_width": 0,
            "padding": 10,
            "margin": 0,
        },
        DEBUG=DEBUG,
    )


def get_github_panel(size=(800, 480)):
    return GithubPanel(
        width=size[0],
        height=size[1],
        settings={
            "username": "TEST_USERNAME",
            "github_token": GITHUB_TOKEN,
            "font": TEST_FONT,
            "font_size": 24,
            "font_color": "black",
            "border_width": 0,
            "padding": 5,
        },
        DEBUG=DEBUG,
    )


def test_picture_panel():
    panel = get_picture_panel()
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

    text_panel = get_text_panel(size)

    time_panel = get_time_panel(size)

    toggl_panel = get_toggl_panel(size)

    calendar_panel = get_calendar_panel(size)

    github_panel = get_github_panel(size)

    panel.set_panels(github_panel, time_panel, toggl_panel, calendar_panel)
    image = panel.draw()

    return image


def test_calendar_panel():

    panel = get_calendar_panel()
    image = panel.draw()

    return image


import sys
import os


if __name__ == "__main__":
    image = test_four_panel()
    # image = test_picture_panel()
    # image = test_calendar_panel()

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
