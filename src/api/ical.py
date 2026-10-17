import logging
from datetime import datetime, timedelta, time

from icalendar import Calendar

import src.default as Default
from src.api import request
from src.helper import resolve_path


logger = logging.getLogger(__name__)


def get_events(ical_urls, use_cache=False) -> list:
    """Return future events from all URLs. Raise when all URLs fail."""
    logger.debug("Fetching events from iCal URLs")

    if use_cache:
        cached_calendar = _load_cache()
        if cached_calendar:
            logger.debug("> Cached calendar loaded successfully")
            return _extract_events(cached_calendar)

    if not isinstance(ical_urls, list):
        ical_urls = [ical_urls]

    calendar = None
    error = None
    for ical_url in ical_urls:
        try:
            logger.debug(f"> Fetching events from iCal URL: {ical_url}")
            temp_calendar = Calendar.from_ical(request("GET", ical_url).content)
        except Exception as e:
            logger.error(f"> Error fetching {ical_url}: {e}")
            error = e
            continue

        if calendar is None:
            calendar = temp_calendar
        else:
            for component in temp_calendar.walk("vevent"):
                calendar.add_component(component)

    if calendar is None:
        raise error or ValueError("No iCal URLs")

    if use_cache:
        _save_cache(calendar)

    events = _extract_events(calendar)
    logger.debug(f"> Extracted {len(events)} events from calendar")

    return events


def _extract_events(calendar, only_future=True):
    now = datetime.now().astimezone()

    events = []
    for component in calendar.walk("vevent"):
        start = component.get("dtstart")
        end = component.get("dtend")
        if not start or not end:
            continue

        event = _format_event(
            {
                "description": component.get("description") or "",
                "summary": component.get("summary") or "",
                "start": start.dt,
                "end": end.dt,
            }
        )

        if only_future and event["end"] < now:
            continue

        events.extend(_divide_event(event))

    return sorted(events, key=lambda x: x["start"])


# ----- Cache Management -----
def _cache_file():
    return resolve_path(Default.CACHE_DIR) / "calendar_cache.ics"


def _save_cache(calendar):
    logger.debug(f"> Saving calendar cache to {_cache_file()}")
    _cache_file().parent.mkdir(parents=True, exist_ok=True)
    _cache_file().write_bytes(calendar.to_ical())


def _load_cache():
    try:
        return Calendar.from_ical(_cache_file().read_bytes())
    except FileNotFoundError:
        logger.info("> No calendar cache found")
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

    # Count calendar days. An end at exactly 00:00 does not start a new day.
    total_days = (event["end"].date() - event["start"].date()).days
    if event["end"].time() != time.min:
        total_days += 1
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
