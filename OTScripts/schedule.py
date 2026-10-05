from datetime import datetime, timedelta
import json
import credentials
import os

class Event:
    def __init__(self, first: datetime, duration: timedelta, repeat: timedelta = None, repeat_until: datetime = None, name: str = ""):
        self.first = first
        self.duration = duration
        self.repeat = repeat
        self.repeat_until = repeat_until
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


def schedule_events(until: datetime):
    schedule = []

    e = Event(
        first=datetime(2026, 9, 1),
        duration=timedelta(hours=7),
        repeat=timedelta(days=1),
        name="speep"
    )
    add_to_schedule(e, until, schedule)

    # Classes
    e = Event(
        first=datetime(2026, 9, 21, hour=9),
        duration=timedelta(hours=2),
        repeat=timedelta(days=7),
        name="therapy class"
    )
    add_to_schedule(e, until, schedule)
    e = Event(
        first=datetime(2026, 9, 21, hour=11),
        duration=timedelta(hours=2),
        repeat=timedelta(days=14),
        name="psychology class"
    )
    add_to_schedule(e, until, schedule)
    e = Event(
        first=datetime(2026, 9, 24, hour=9, minute=30),
        duration=timedelta(hours=2),
        repeat=timedelta(days=7),
        name="stats class"
    )
    add_to_schedule(e, until, schedule)
    e = Event(
        first=datetime(2026, 9, 29, hour=9),
        duration=timedelta(hours=2),
        repeat=timedelta(days=7),
        name="psychology class"
    )
    add_to_schedule(e, until, schedule)

    # Societies

    # One time

    return schedule

def main():
    schedule = schedule_events(datetime(2026, 10, 31))
    schedule = sort_schedule(schedule)
    print(schedule)

    # Upload to front end
    upload_to = os.path.join("Resources", "Schedule", "schedule.json")
    upload_url = "https://neocities.org/api/upload"
    neocities_header = {"Authorization": f"Bearer {credentials.neocities_api}"}


def upload_files(files: List[Tuple[str, str]]):
    print(f"Pushing: {repr(files)}")

    # Get the file data from the path, and write it to the chunk
    files_data = {pair[0]: open(pair[1], 'rb') for pair in files}
    request = requests.post(upload_url, headers=neocities_header, files=files_data)
    if request.status_code == 200:
        return request.status_code

    print(f"Failed to post to {upload_url}\nstatus code: {request.status_code}\nresponse: {request.text}")
    return request.status_code

if __name__ == "__main__":
    main()