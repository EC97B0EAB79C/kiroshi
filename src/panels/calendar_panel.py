from PIL import Image, ImageDraw, ImageFont
from datetime import date, datetime, timedelta, time

from src.panel import Panel
import src.helper as Helper
from src.palette import *
import src.default as Default

import src.api.ical as IcalAPI


class CalendarPanel(Panel):
    def __init__(self, width, height, settings, DEBUG=False):
        super().__init__(width, height, settings, DEBUG)

        # Text settings
        self.font = settings.get("font", Default.FONT_EMOJI)
        self.font_size = settings.get("font_size", Default.FONT_SIZE["p"])

        # Calendar settings
        self.ical_urls = settings.get("ical_urls")

        # Margin, padding and border settings
        self.padding = settings.get("padding", Default.PADDING)
        self.entry_padding = settings.get("entry_padding", Default.PADDING_CONTENT)

        # Request settings
        self.request_interval = settings.get("request_interval", 0)
        self.request_recent = datetime.min
        self.cache = None

    def _request(self):
        if (self.cache is not None) and (
            datetime.now() - self.request_recent
            < timedelta(minutes=self.request_interval)
        ):
            return self.cache

        events = IcalAPI.get_events(self.ical_urls)
        self.cache = events
        self.request_recent = datetime.now()

        return self.cache

    def _draw(self, image):
        draw = ImageDraw.Draw(image)

        spacing = self.padding + self.margin

        font = Helper.load_font(self.font, self.font_size)

        events = self._request()
        if not events:
            return image

        today = datetime.combine(date.today(), datetime.min.time()).astimezone()
        events = [
            event for event in events if (event["start"] and event["start"] >= today)
        ]

        current_month = None
        current_day = None
        current_week = None
        event_spacing = font.getbbox("000")[2]
        location = (spacing, spacing)
        for event in events:
            if location[1] > self.height - spacing * 2:
                break

            start = event["start"]
            if start.month != current_month:
                current_month = start.month
                location = self._draw_month(image, start, font, location, event_spacing)
            if start.isocalendar()[1] != current_week:
                current_week = start.isocalendar()[1]
                location = self._draw_week(
                    image, current_week, font, location, event_spacing
                )
            if start.day != current_day:
                current_day = start.day
                location = self._draw_day(image, start, font, location)

            location = self._draw_entry(image, event, font, location, event_spacing)

        draw.rectangle(
            [(0, self.height - spacing), (self.width, self.height)], fill="white"
        )
        return super()._draw(image)

    def _draw_month(self, image, month, font, location, spacing):
        text = month.strftime("%Y %B")
        bbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox(
            (0, 0), text, font=font
        )
        position = (
            location[0] - bbox[0] + spacing,
            location[1] - bbox[1],
        )
        draw = ImageDraw.Draw(image)
        draw.text(
            position,
            text,
            font=font,
            fill="black",
        )
        return (location[0], location[1] + bbox[3] - bbox[1] + self.padding)

    def _draw_week(self, image, week, font, location, spacing):
        text = f"Week {week}"
        bbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox(
            (0, 0), text, font=font
        )
        position = (
            location[0] - bbox[0] + spacing,
            location[1] - bbox[1],
        )
        draw = ImageDraw.Draw(image)
        draw.text(
            position,
            text,
            font=font,
            fill="black",
        )
        return (location[0], location[1] + bbox[3] - bbox[1] + self.padding)

    def _draw_day(self, image, day, font, location):
        is_today = day.date() == date.today()
        text = day.strftime("%d")
        bbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox(
            (0, 0), text, font=font
        )
        position = (
            location[0] - bbox[0],
            location[1] - bbox[1],
        )
        draw = ImageDraw.Draw(image)

        if is_today:
            draw.circle(
                (
                    location[0] + (bbox[2] - bbox[0]) // 2,
                    location[1] + (bbox[3] - bbox[1]) // 2,
                ),
                radius=(bbox[2] - bbox[0]) // 2 + self.entry_padding,
                fill=PALETTE_GREEN,
            )
        text_fill = "white" if is_today else "black"
        draw.text(
            position,
            text,
            font=font,
            fill=text_fill,
        )
        return (location[0], location[1])

    def _draw_entry(self, image, entry, font, location, spacing):
        entry_width = self.width - location[0] - spacing * 2
        text = entry["summary"]
        text = Helper.truncate_text(text, font, entry_width)
        if not self._is_fullday_event(entry):
            text += (
                f"\n{entry['start'].strftime('%H:%M')}-{entry['end'].strftime('%H:%M')}"
            )
        bbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox(
            (0, 0), text, font=font
        )
        position = (
            location[0] + spacing,
            location[1] - bbox[1],
        )
        fill_color = "black"
        if (
            self.palette_name == "6_colors"
            and entry["description"]
            and "holiday" in entry["description"].lower()
        ):
            fill_color = PALETTE_RED

        draw = ImageDraw.Draw(image)
        draw.rectangle(
            [
                (
                    position[0] - self.entry_padding,
                    position[1] - self.entry_padding + bbox[1],
                ),
                (
                    position[0] + entry_width + self.entry_padding,
                    position[1] + bbox[3] + self.entry_padding,
                ),
            ],
            fill=fill_color,
        )
        draw.text(
            position,
            text,
            font=font,
            fill="white",
        )
        return (
            location[0],
            location[1] + bbox[3] - bbox[1] + self.padding + 2 * self.entry_padding,
        )

    def _is_fullday_event(self, entry):
        start = entry["start"]
        if not (start.hour == 0 and start.minute == 0):
            return False

        end = entry["end"]
        if not (end.hour == 0 and end.minute == 0):
            return False

        return True
