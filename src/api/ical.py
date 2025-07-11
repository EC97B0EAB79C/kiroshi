import requests
from icalendar import Calendar
from datetime import date, datetime, timedelta
import os


def get_events(ical_url, use_cache=False):
    if use_cache:
        cached_calendar = _load_cache()
        if cached_calendar:
            return _extract_events(cached_calendar)

    response = requests.get(ical_url)
    if response.status_code == 200:
        calendar = Calendar.from_ical(response.content)
        _save_cache(calendar)
        return _extract_events(calendar)
    return None


def _extract_events(calendar):
    events = []
    for component in calendar.walk("vevent"):
        event = {
            "summary": component.get("summary"),
            "start": (
                component.get("dtstart").dt if component.get("dtstart") else None
            ),
            "end": component.get("dtend").dt if component.get("dtend") else None,
        }
        if isinstance(event["start"], datetime):
            event["start"] = event["start"].date()
        if isinstance(event["end"], datetime):
            event["end"] = event["end"].date()
        events.append(event)
    return events


# ----- Cache Management -----
def _save_cache(calendar):
    with open(".cache/calendar_cache.ics", "wb") as f:
        f.write(calendar.to_ical())


def _load_cache():
    try:
        os.makedirs(".cache", exist_ok=True)
        with open(".cache/calendar_cache.ics", "rb") as f:
            return Calendar.from_ical(f.read())
    except FileNotFoundError:
        return None


if __name__ == "__main__":
    ical_url = "https://calendar.google.com/calendar/ical/en.japanese%23holiday%40group.v.calendar.google.com/public/basic.ics"
    events = get_events(ical_url, use_cache=True)

    today = date.today()
    end = today + timedelta(days=30)

    for event in events:
        if not event["start"]:
            continue

        if today <= event["start"] < end:
            print(f"Event: {event['summary']}")
            print(f"Start: {event['start']}")
            print(f"End: {event['end']}")
            print("-" * 20)
