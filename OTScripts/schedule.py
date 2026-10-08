from datetime import datetime, timedelta
import datetime as dt
import json
import os
import helpers
import pytz

timezone = pytz.timezone("Europe/London")
class Event:
    def __init__(self, first: datetime, duration: timedelta, category: str, repeat: timedelta = None, repeat_until: datetime = None, name: str = ""):
        self.first = timezone.localize(first)
        self.duration = duration
        self.repeat = repeat
        self.repeat_until = None
        if repeat_until is not None:
            self.repeat_until = timezone.localize(repeat_until)
        self.name = name
        self.category = category

    @staticmethod
    def serialize(event: 'Event', at: datetime):
        return {
            "time": at.timestamp(),
            "duration": event.duration.total_seconds(),
            "name": event.name,
            "category": event.category,
        }


def add_to_schedule(event: Event, until: datetime, schedule_unsorted):
    curr_time = event.first
    end = until
    if event.repeat_until is not None and event.repeat_until < end:
        end = event.repeat_until

    while curr_time < end:
        schedule_unsorted.append(Event.serialize(event, curr_time))
        if event.repeat is None:
            break
        curr_time += event.repeat


def sort_schedule(unsorted_schedule):
    key = lambda event: event["time"]
    return sorted(unsorted_schedule, key=key)


def schedule_events(until: datetime):
    schedule = []

    e = Event(
        first=datetime(2026, 9, 1),
        duration=timedelta(hours=7),
        repeat=timedelta(days=1),
        name="stalking the shadows",
        category="sleep",
    )
    add_to_schedule(e, until, schedule)

    # Classes
    e = Event(
        first=datetime(2026, 9, 21, hour=9),
        duration=timedelta(hours=2),
        repeat=timedelta(days=7),
        name="mind control study",
        category="work",
    )
    add_to_schedule(e, until, schedule)
    e = Event(
        first=datetime(2026, 9, 21, hour=11),
        duration=timedelta(hours=2),
        repeat=timedelta(days=14),
        name="behaviour control",
        category="work",
    )
    add_to_schedule(e, until, schedule)
    e = Event(
        first=datetime(2026, 9, 24, hour=9, minute=30),
        duration=timedelta(hours=2),
        repeat=timedelta(days=7),
        name="stats.",
        category="work",
    )
    add_to_schedule(e, until, schedule)
    e = Event(
        first=datetime(2026, 9, 29, hour=9),
        duration=timedelta(hours=2),
        repeat=timedelta(days=14),
        name="behaviour control",
        category="work",
    )
    add_to_schedule(e, until, schedule)

    # Societies
    e = Event(
        first=datetime(2026, 10, 6, hour=18),
        duration=timedelta(hours=3),
        repeat=timedelta(days=7),
        name="on the table",
        category="community",
    )
    add_to_schedule(e, until, schedule)

    e = Event(
        first=datetime(2026, 10, 5, hour=18),
        duration=timedelta(hours=3),
        repeat=timedelta(days=7),
        name="gay",
        category="community",
    )
    add_to_schedule(e, until, schedule)

    e = Event(
        first=datetime(2026, 10, 9, hour=18),
        duration=timedelta(hours=3),
        repeat=timedelta(days=7),
        name="furry",
        category="community",
    )
    add_to_schedule(e, until, schedule)

    # One time
    e = Event(
        first=datetime(2026, 10, 12, hour=7, minute=0),
        duration=timedelta(hours=17),
        repeat=None,
        name="deer",
        category="event",
    )
    add_to_schedule(e, until, schedule)

    e = Event(
        first=datetime(2026, 10, 8, hour=19, minute=0),
        duration=timedelta(hours=3),
        repeat=None,
        name="furry games",
        category="event",
    )
    add_to_schedule(e, until, schedule)
    
    e = Event(
        first=datetime(2026, 10, 6, hour=14, minute=15),
        duration=timedelta(hours=1),
        repeat=None,
        name="",
        category="appointment",
    )
    add_to_schedule(e, until, schedule)

    e = Event(
        first=datetime(2026, 10, 12, hour=15, minute=15),
        duration=timedelta(hours=1),
        repeat=None,
        name="chomper assessment",
        category="appointment",
    )
    add_to_schedule(e, until, schedule)

    return schedule

def main():
    until = datetime(2026, 11, 30, tzinfo=timezone)
    schedule = schedule_events(until)
    schedule = sort_schedule(schedule)
    dat = {
        "updated": datetime.now(timezone).timestamp(),
        "until": until.timestamp(),
        "schedule": schedule
    }

    # Upload to front end
    upload_to = os.path.join("Resources", "Schedule", "schedule.json")
    helpers.upload_file_data({
        upload_to: json.dumps(dat)
    })

if __name__ == "__main__":
    main()