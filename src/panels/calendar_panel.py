from datetime import date

from PIL import ImageDraw

from src.panel import Panel
import src.helper as Helper
from src.palette import PALETTE_GREEN, PALETTE_RED
import src.default as Default

import src.api.ical as IcalAPI


class CalendarPanel(Panel):
    def __init__(self, width, height, settings=None, debug=False):
        super().__init__(width, height, settings, debug)
        settings = self.settings

        # Text settings
        self.font = settings.get("font", Default.FONT_EMOJI)
        self.font_size = settings.get("font_size", Default.FONT_SIZE["p"])

        # Calendar settings
        self.ical_urls = settings.get("ical_urls")

        self.entry_padding = settings.get("entry_padding", Default.PADDING_CONTENT)

        # Refresh settings: (day, events) on the display now
        self.drawn = None

    def _draw(self, image):
        draw = ImageDraw.Draw(image)

        spacing = self.padding + self.margin

        font = Helper.load_font(self.font, self.font_size)

        events = self.cached_request(lambda: IcalAPI.get_events(self.ical_urls))
        if events is None:
            image = Helper.invalid_image(
                image, self.width, self.height, Helper.error_text("Calendar error", self.error)
            )
            return super()._draw(image)

        current_month = None
        current_day = None
        current_week = None
        event_spacing = font.getbbox("000")[2]
        location = (spacing, spacing)
        displayed_events = []
        for event in events:
            if location[1] > self.height - spacing * 2:
                break

            displayed_events.append(event)

            start = event["start"]
            if (start.year, start.month) != current_month:
                current_month = (start.year, start.month)
                location = self._draw_month(image, start, font, location, event_spacing)
            if start.isocalendar()[:2] != current_week:
                current_week = start.isocalendar()[:2]
                location = self._draw_week(
                    image, current_week[1], font, location, event_spacing
                )
            if start.date() != current_day:
                current_day = start.date()
                location = self._draw_day(image, start, font, location)

            location = self._draw_entry(image, event, font, location, event_spacing)

        draw.rectangle(
            [(0, self.height - spacing), (self.width, self.height)], fill="white"
        )

        # Refresh when the events or the day ("today" mark) change
        drawn = (date.today(), displayed_events)
        if self.drawn != drawn:
            self.drawn = drawn
            self.refresh = True

        return super()._draw(image)

    def _draw_month(self, image, month, font, location, spacing):
        text = month.strftime("%Y %B")
        bbox = Helper.text_bbox(text, font)
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
        bbox = Helper.text_bbox(text, font)
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
        bbox = Helper.text_bbox(text, font)
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
        bbox = Helper.text_bbox(text, font)
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
