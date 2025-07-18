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
            "description": component.get("description") or "",
            "summary": component.get("summary") or "",
            "start": (
                component.get("dtstart").dt if component.get("dtstart") else None
            ),
            "end": component.get("dtend").dt if component.get("dtend") else None,
        }
        if not event["start"] or not event["end"]:
            continue

        event = _format_event(event)
        divided_events = _divide_event(event)
        events.extend(divided_events)

    events = sorted(events, key=lambda x: x["start"])
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


# ----- Helper Functions -----
def _format_event(event):
    if isinstance(event["start"], datetime):
        event["start"] = event["start"].astimezone()
    else:
        event["start"] = datetime.combine(
            event["start"], datetime.min.time()
        ).astimezone()
    if isinstance(event["end"], datetime):
        event["end"] = event["end"].astimezone()
    else:
        event["end"] = datetime.combine(event["end"], datetime.min.time()).astimezone()

    return event


def _divide_event(event):
    events = []
    midnight = datetime.combine(
        event["start"].date() + timedelta(days=1), time.min
    ).astimezone()

    if event["end"] <= midnight:
        return [event]

    total_days = (event["end"] - event["start"]).days + 1
    idx = 1
    temp_start = event["start"]
    temp_end = midnight
    while temp_end < event["end"]:
        events.append(
            {
                "summary": f"{event['summary']} ({idx}/{total_days})",
                "description": event["description"],
                "start": temp_start,
                "end": temp_end,
            }
        )
        temp_start = temp_end
        temp_end += timedelta(days=1)
        idx += 1
    event["summary"] = f"{event.get('summary', '')} ({idx}/{total_days})"
    event["start"] = temp_start

    events.append(event)
    return events


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
