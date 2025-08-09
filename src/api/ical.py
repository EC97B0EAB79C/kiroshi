import logging
import requests
from icalendar import Calendar
from datetime import date, datetime, timedelta, time
import os


logger = logging.getLogger(__name__)


def get_events(ical_urls, use_cache=False):
    logger.debug("Fetching events from iCal URLs")

    # Load cached calendar if requested
    if use_cache:
        logger.debug("> Loading cached calendar")
        cached_calendar = _load_cache()
        if cached_calendar:
            logger.debug("> Cached calendar loaded successfully")
            return _extract_events(cached_calendar)
        logger.debug("> No cached calendar found")

    if not isinstance(ical_urls, list):
        ical_urls = [ical_urls]

    logger.debug(f"> Fetching events from {len(ical_urls)} iCal URLs")
    calendar = None
    for ical_url in ical_urls:
        try:
            logger.debug(f"> Fetching events from iCal URL: {ical_url}")
            response = requests.get(ical_url)
            logger.debug(f"> API response status code: {response.status_code}")

            response.raise_for_status()
            if calendar is None:
                calendar = Calendar.from_ical(response.content)
            else:
                temp_calendar = Calendar.from_ical(response.content)
                for component in temp_calendar.walk("vevent"):
                    calendar.add_component(component)

        except Exception as e:
            logger.error(f"> Error fetching {ical_url}: {e}")

    if calendar is None:
        return []

    if use_cache:
        _save_cache(calendar)

    events = _extract_events(calendar)
    logger.debug(f"> Extracted {len(events)} events from calendar")

    return events


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
    logger.debug("> Saving calendar cache to .cache/calendar_cache.ics")
    with open(".cache/calendar_cache.ics", "wb") as f:
        f.write(calendar.to_ical())
        logger.debug("> Calendar cache saved successfully")


def _load_cache():
    try:
        logger.debug("> Loading calendar cache from .cache/calendar_cache.ics")
        os.makedirs(".cache", exist_ok=True)
        with open(".cache/calendar_cache.ics", "rb") as f:
            return Calendar.from_ical(f.read())
    except FileNotFoundError:
        logger.error("> No calendar cache found")
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
