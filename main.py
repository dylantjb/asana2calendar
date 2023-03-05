"""Fetch tasks from project and creates an event in respective caldav calendar."""
import configparser
import os
from datetime import date, datetime, timedelta
from inspect import signature

import asana
import caldav

config = configparser.ConfigParser()
if "XDG_CONFIG_DIR" in os.environ:
    config.read(str(os.environ["XDG_CONFIG_DIR"] + "/asana2calendar/config.ini"))
else:
    config.read(str(os.environ["HOME"] + "/.config/asana2calendar/config.ini"))
settings = dict(config.items("asana2calendar"))


class Task:
    def __init__(self, gid, name, due_on, start_on, modified_on, completed):
        self._id = gid
        self._name = name
        self._due_on = due_on
        self._start_on = start_on
        self._modified_on = modified_on
        self._completed = completed

    def __str__(self):
        return {
            "gid": self._id,
            "name": self._name,
            "due_on": self._due_on,
            "start_on": self._start_on,
            "modified_on": self._modified_on,
            "completed": self._completed,
            "resource_type": "task",
            "resource_subtype": "default_task",
        }

    @staticmethod
    def convert_datetime(date_str):
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")

    @staticmethod
    def convert_datestr(date_time):
        return date_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def due_on(self):
        return self.convert_datetime(self._due_on)

    @due_on.setter
    def due_on(self, due_on):
        self._due_on = self.convert_datestr(due_on)

    @property
    def start_on(self):
        return self.convert_datetime(self._start_on)

    @start_on.setter
    def start_on(self, start_on):
        self._start_on = self.convert_datestr(start_on)

    @property
    def modified_on(self):
        return self.convert_datetime(self._modified_on)

    @modified_on.setter
    def modified_on(self, modified_on):
        self._modified_on = self.convert_datestr(modified_on)

    @property
    def completed(self):
        return self._completed

    @completed.setter
    def completed(self, completed):
        self._completed = completed


class Project:
    """Represents an asana project and modify tasks."""

    def __init__(self, token, name):
        self._client = asana.Client.access_token(token)
        self._client.headers = {"asana-enable": "new_memberships"}
        self._project_id = self.get_project_id(name)

    def get_project_id(self, name):
        """Obtains all projects owned by user and finds the associated ID, using name as a filter.

        Returns associated asana project ID.
        """
        projects = self._client.projects.get_projects(
            offset=None, iterator_type=None, opt_fields=["name"]
        )
        return [p for p in projects if p["name"] == name][0]["gid"]

    def get_tasks(self):
        """Obtains all henceforth tasks associated with the project.
        Retrieves other useful fields.

        Returns Task objects representing asana tasks.
        """
        fields = list(signature(Task.__init__).parameters.keys())[1:]
        return [
            Task(*map(task.get, fields))
            for task in self._client.tasks.get_tasks_for_project(
                self._project_id,
                opt_fields=fields
                + [
                    "sort_by=due_date",
                    f"due_on.after={datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')}",
                ],
            )
        ]

    def create_tasks(self, *tasks):
        """Creates tasks with supplied metadata in the project."""
        for task in tasks:
            self._client.tasks.create_task(str(task) | {"projects": self._project_id})

    def delete_tasks(self, *tasks):
        """Delete tasks from project using task ID."""
        for task in tasks:
            self._client.tasks.delete(task.id)

    def update_tasks(self, *tasks):
        """Update tasks with supplied metadata in the project."""
        for task in tasks:
            self._client.tasks.update(task.id, str(task))


def main(principle, name):
    """Opens the caldav client and runs sync operations."""
    proj = Project(os.environ["ASANA_CLIENT_ID"], name)
    if any(c.name == name for c in principle.calendars()):
        cal = principle.calendar(name=name)
    else:
        cal = principle.make_calendar(name=name)

    # How would you know task/event has been deleted? -- save state since last sync
    # How would you know if task/event has just been created? -- keep a list of IDs

    # Loop through tasks
    # IF task has no link to event THEN create event in caldav
    # IF task has (matching name AND matching due/start dates) THEN
    #   Check if fields are different and prioritise modified time
    #   Update changed fields (name, location, description, completed)

    # Update changes on caldav

    # Loop through caldav events
    # IF has event no link in caldav THEN create task in project

    tasks = proj.get_tasks()
    for i in tasks:
        print(i.name)
    events = cal.search(
        start=datetime.now(),
        end=datetime(date.today().year + 1, 1, 1),
        event=True,
        expand=True,
    )


if __name__ == "__main__":
    if "ASANA_CLIENT_ID" in os.environ:
        with caldav.DAVClient(
            url=settings["url"],
            username=settings["username"],
            password=settings["password"],
        ) as client:
            main(client.principal(), settings["name"])
    else:
        print("Set 'ASANA_CLIENT_ID' environment variable before running.")

# TODO: Handle if caldav connection fails
#       Handle if config is unreachable
