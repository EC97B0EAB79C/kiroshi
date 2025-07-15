import requests
from icalendar import Calendar
from datetime import date, datetime, timedelta, time
import os


def get_events(ical_urls, use_cache=False):
    if use_cache:
        cached_calendar = _load_cache()
        if cached_calendar:
            return _extract_events(cached_calendar)

    if not isinstance(ical_urls, list):
        ical_urls = [ical_urls]

    calendar = None
    for ical_url in ical_urls:
        try:
            response = requests.get(ical_url)
            response.raise_for_status()
            if calendar is None:
                calendar = Calendar.from_ical(response.content)
            else:
                temp_calendar = Calendar.from_ical(response.content)
                for component in temp_calendar.walk("vevent"):
                    calendar.add_component(component)

        except Exception as e:
            print(f"Error fetching {ical_url}: {e}")

    if use_cache and calendar:
        _save_cache(calendar)

    return _extract_events(calendar) if calendar else []


def _extract_events(calendar):
    events = []
    for component in calendar.walk("vevent"):
        event = {
            "description": component.get("description"),
            "summary": component.get("summary"),
            "start": (
                component.get("dtstart").dt if component.get("dtstart") else None
            ),
            "end": component.get("dtend").dt if component.get("dtend") else None,
        }
        if isinstance(event["start"], date):
            event["start"] = datetime.combine(event["start"], datetime.min.time())
        if isinstance(event["end"], date):
            event["end"] = datetime.combine(event["end"], datetime.min.time())
        events.append(event)

    # TODO cut multiday events
    events = sorted(events, key=lambda x: x["start"] or datetime.max)
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


TEST_DATA = [
    {
        "summary": "Test Event 1",
        "start": datetime.combine(date.today(), time(10, 0)),
        "end": datetime.combine(date.today(), time(11, 0)),
    },
    {
        "summary": "Test Event 2",
        "start": datetime.combine(date.today() + timedelta(days=1), time(12, 0)),
        "end": datetime.combine(date.today() + timedelta(days=1), time(13, 0)),
    },
    {
        "summary": "Test Event 2-1 very long title that should be truncated",
        "start": datetime.combine(date.today() + timedelta(days=1), time(13, 0)),
        "end": datetime.combine(date.today() + timedelta(days=1), time(15, 0)),
    },
    {
        "summary": "Test Event 3 - H",
        "start": datetime.combine(date.today() + timedelta(days=3), time(0, 0)),
        "end": datetime.combine(date.today() + timedelta(days=4), time(0, 0)),
    },
    # {
    #     "summary": "Test Event 3",
    #     "start": datetime.combine(date.today() + timedelta(days=3), time(14, 0)),
    #     "end": datetime.combine(date.today() + timedelta(days=3), time(15, 0)),
    # },
    {
        "summary": "Test Event 4",
        "start": datetime.combine(date.today() + timedelta(days=32), time(14, 0)),
        "end": datetime.combine(date.today() + timedelta(days=32), time(15, 0)),
    },
]

if __name__ == "__main__":
    ical_url = [
        "https://calendar.google.com/calendar/ical/en.japanese%23holiday%40group.v.calendar.google.com/public/basic.ics",
        "https://calendar.google.com/calendar/ical/en.south_korea%23holiday%40group.v.calendar.google.com/public/basic.ics",
    ]
    events = get_events(ical_url, use_cache=False)

    today = datetime.combine(date.today(), datetime.min.time())
    end = today + timedelta(days=90)

    for event in events:
        if not event["start"]:
            continue

        if today <= event["start"] < end:
            print(f"Event: {event['summary']}")
            print(f"Description: {event['description']}")
            print(f"Start: {event['start']}")
            print(f"End: {event['end']}")
            print("-" * 20)
