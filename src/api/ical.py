import requests
from icalendar import Calendar
from datetime import datetime, timedelta


def get_events(ical_url):
    response = requests.get(ical_url)
    if response.status_code == 200:
        calendar = Calendar.from_ical(response.content)
        events = []
        for component in calendar.walk("vevent"):
            print(component)
            exit()
            event = {
                "summary": component.get("summary"),
                "start": component.get("dtstart"),
                "end": component.get("dtend"),
            }
            events.append(event)
        return events
    return None


if __name__ == "__main__":
    ical_url = ""
    events = get_events(ical_url)

    local_tz = datetime.now().astimezone().tzinfo
    for event in events:
        print(f"Event: {event['summary']}")
        print(f"Start: {event['start']}")
        print(f"End: {event['end']}")
        print("-" * 20)
