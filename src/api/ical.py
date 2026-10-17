import asyncio
import hashlib
import logging
from datetime import datetime, timedelta, time

from icalendar import Calendar

from src.api import async_request

logger = logging.getLogger(__name__)

# URL -> (request headers, content hash, events). Parse a calendar only when it changes.
_cache = {}


async def get_events(ical_urls) -> list:
    """Return future events from all URLs, read at the same time. Raise when all URLs fail."""
    if not isinstance(ical_urls, list):
        ical_urls = [ical_urls]
    if not ical_urls:
        raise ValueError("No iCal URLs")

    results = await asyncio.gather(*map(_get_url_events, ical_urls), return_exceptions=True)
    errors = [r for r in results if isinstance(r, Exception)]
    for url, result in zip(ical_urls, results):
        if isinstance(result, Exception):
            logger.error(f"> Error fetching {url}: {result}")
    if len(errors) == len(results):
        raise errors[0]

    now = datetime.now().astimezone()
    events = [
        event
        for result in results
        if not isinstance(result, Exception)
        for event in result
        if event["end"] >= now
    ]
    logger.debug(f"> {len(events)} future events")
    return sorted(events, key=lambda x: x["start"])


async def _get_url_events(url) -> list:
    headers, digest, events = _cache.get(url, ({}, None, None))
    response = await async_request("GET", url, headers=headers)
    if response.status_code == 304:
        return events

    new_digest = hashlib.sha256(response.content).hexdigest()
    if new_digest != digest:
        logger.debug(f"> Parsing {url}")
        events = await asyncio.to_thread(_parse, response.content)

    validators = {"If-None-Match": response.headers.get("ETag"), "If-Modified-Since": response.headers.get("Last-Modified")}
    _cache[url] = ({k: v for k, v in validators.items() if v}, new_digest, events)
    return events


def _parse(content) -> list:
    return _extract_events(Calendar.from_ical(content))


def _extract_events(calendar) -> list:
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
        events.extend(_divide_event(event))

    return events


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
