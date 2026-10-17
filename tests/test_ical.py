import unittest
from datetime import date, datetime, timedelta
from unittest.mock import patch

from icalendar import Calendar, Event

from src.api import ical


def local(*args):
    return datetime(*args).astimezone()


class TestIcal(unittest.TestCase):
    def test_format_all_day_event(self):
        event = ical._format_event({"start": date(2026, 1, 1), "end": date(2026, 1, 2)})
        self.assertEqual(event["start"], local(2026, 1, 1))
        self.assertEqual(event["end"], local(2026, 1, 2))

    def test_one_day_event_is_not_divided(self):
        event = {"summary": "A", "description": "", "start": local(2026, 1, 1, 10), "end": local(2026, 1, 1, 12)}
        self.assertEqual(ical._divide_event(dict(event)), [event])

    def test_all_day_events_are_divided(self):
        event = {"summary": "A", "description": "", "start": local(2026, 1, 1), "end": local(2026, 1, 3)}
        parts = ical._divide_event(event)
        self.assertEqual([p["summary"] for p in parts], ["A (1/2)", "A (2/2)"])
        self.assertEqual(parts[1]["start"], local(2026, 1, 2))

    def test_overnight_event_is_divided(self):
        event = {"summary": "A", "description": "", "start": local(2026, 1, 1, 23), "end": local(2026, 1, 2, 1)}
        parts = ical._divide_event(event)
        self.assertEqual([p["summary"] for p in parts], ["A (1/2)", "A (2/2)"])

    def test_extract_events_only_future_and_sorted(self):
        calendar = Calendar()
        tomorrow = datetime.now().astimezone() + timedelta(days=1)
        for summary, start in [("later", tomorrow + timedelta(hours=2)), ("soon", tomorrow), ("past", tomorrow - timedelta(days=10))]:
            event = Event()
            event.add("summary", summary)
            event.add("dtstart", start)
            event.add("dtend", start + timedelta(minutes=30))
            calendar.add_component(event)

        events = ical._extract_events(calendar)
        self.assertEqual([e["summary"] for e in events], ["soon", "later"])

    @patch("src.api.ical.request", side_effect=ConnectionError("down"))
    def test_all_urls_fail_raises(self, _):
        with self.assertRaises(ConnectionError):
            ical.get_events(["https://a.example/a.ics", "https://b.example/b.ics"])


if __name__ == "__main__":
    unittest.main()
