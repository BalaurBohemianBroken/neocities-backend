from datetime import datetime, timedelta
import datetime
import json
import os
import helpers
import pytz

timezone = pytz.timezone("Europe/London")
class Event:
    def __init__(self, first: datetime, duration: timedelta, repeat: timedelta = None, repeat_until: datetime = None, name: str = ""):
        self.first = first.localize(timezone)
        self.duration = duration
        self.repeat = repeat
        self.repeat_until = repeat_until.localize(timezone)
        self.name = name

    @staticmethod
    def serialize(event: 'Event', at: datetime):
        return {
            "time": at.timestamp(),
            "duration": event.duration.total_seconds(),
            "name": event.name
        }


def add_to_schedule(event: Event, until: datetime, schedule_unsorted):
    curr_time = event.first
    end = until
    if event.repeat_until is not None and event.repeat_until < end:
        end = event.repeat_until

    while curr_time < end:
        schedule_unsorted.append(Event.serialize(event, curr_time))
        curr_time += event.repeat


def sort_schedule(unsorted_schedule):
    key = lambda event: event["time"]
    return sorted(unsorted_schedule, key=key)


def schedule_events(until: datetime, timezone):
    schedule = []

    e = Event(
        first=datetime(2026, 9, 1),
        duration=timedelta(hours=7),
        repeat=timedelta(days=1),
        name="stalking the shadows"
    )
    add_to_schedule(e, until, schedule)

    # Classes
    e = Event(
        first=datetime(2026, 9, 21, hour=9),
        duration=timedelta(hours=2),
        repeat=timedelta(days=7),
        name="mind control study"
    )
    add_to_schedule(e, until, schedule)
    e = Event(
        first=datetime(2026, 9, 21, hour=11),
        duration=timedelta(hours=2),
        repeat=timedelta(days=14),
        name="behaviour control"
    )
    add_to_schedule(e, until, schedule)
    e = Event(
        first=datetime(2026, 9, 24, hour=9, minute=30),
        duration=timedelta(hours=2),
        repeat=timedelta(days=7),
        name="stats."
    )
    add_to_schedule(e, until, schedule)
    e = Event(
        first=datetime(2026, 9, 29, hour=9),
        duration=timedelta(hours=2),
        repeat=timedelta(days=7),
        name="behaviour control"
    )
    add_to_schedule(e, until, schedule)

    # Societies
    e = Event(
        first=datetime(2026, 10, 6, hour=18),
        duration=timedelta(hours=3),
        repeat=timedelta(days=7),
        name="on the table"
    )
    add_to_schedule(e, until, schedule)

    e = Event(
        first=datetime(2026, 10, 5, hour=18),
        duration=timedelta(hours=3),
        repeat=timedelta(days=7),
        name="gay"
    )
    add_to_schedule(e, until, schedule)

    e = Event(
        first=datetime(2026, 10, 9, hour=18),
        duration=timedelta(hours=3),
        repeat=timedelta(days=7),
        name="furry"
    )
    add_to_schedule(e, until, schedule)

    # One time
    e = Event(
        first=datetime(2026, 10, 6, hour=14, minute=15),
        duration=timedelta(hours=1),
        repeat=None,
        name=""
    )
    add_to_schedule(e, until, schedule)

    e = Event(
        first=datetime(2026, 10, 12, hour=15, minute=15),
        duration=timedelta(hours=1),
        repeat=None,
        name="dentist"
    )
    add_to_schedule(e, until, schedule)

    return schedule

def main():
    until = datetime(2026, 11, 30, tzinfo=timezone)
    schedule = schedule_events(until, timezone)
    schedule = sort_schedule(schedule)
    dat = {
        "updated": datetime.now(timezone),
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