# from caldav.elements import cdav, dav
from datetime import date, datetime

import caldav


class CaldavCalendar:
    def __init__(self, principal):
        self.principal = principal
        self.calendars = self.principal.calendars()

    def get_events(
        self, start_date=datetime.now(), end_date=datetime(date.today().year + 1, 1, 1)
    ):
        events = []
        for calendar in self.calendars:
            results = calendar.search(
                start=start_date, end=end_date, event=True, expand=True
            )
            for result in results:
                events.append(
                    {
                        "id": result.instance.href,
                        "summary": result.instance.summary,
                        "description": result.instance.description,
                        "location": result.instance.location,
                        "start_time": result.instance.start_time,
                        "end_time": result.instance.end_time,
                        "last_modified": result.instance.last_modified,
                    }
                )
        return events

    def create_event(self, event):
        calendar = self.calendars[0]  # Use the first calendar for simplicity
        vevent = caldav.Event(calendar, event)
        calendar.add_event(vevent)

    def update_event(self, event):
        calendar = self.calendars[0]  # Use the first calendar for simplicity
        event_id = event["id"]
        vevent = calendar.event_by_url(event_id)
        vevent.load()
        vevent.update(event)
        vevent.save()

    def delete_event(self, event_id):
        calendar = self.calendars[0]  # Use the first calendar for simplicity
        vevent = calendar.event_by_url(event_id)
        vevent.delete()
