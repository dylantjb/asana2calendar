"""Fetch tasks from project and creates an event in respective caldav calendar."""
import configparser
import os
from datetime import date, datetime, timedelta

import asana
import caldav

config = configparser.ConfigParser()
if "XDG_CONFIG_DIR" in os.environ:
    config.read(str(os.environ["XDG_CONFIG_DIR"] + "/asana2caldav/config.ini"))
else:
    config.read(str(os.environ["HOME"] + "/.config/asana2caldav/config.ini"))
settings = dict(config.items("asana2caldav"))


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

        Returns Generator objects representing asana tasks.
        """
        return self._client.tasks.get_tasks_for_project(
            self._project_id,
            opt_fields=[
                "name",
                "due_at",
                "start_at",
                "modified_on",
                "completed",
                "sort_by=due_date"
                f"due_at.after={datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')}",
            ],
        )

    def create_tasks(self, *tasks):
        """Creates tasks with supplied metadata in the project."""
        for task in tasks:
            task["projects"] = self._project_id
            self._client.tasks.create_task(task)

    def delete_tasks(self, *tasks):
        """Delete tasks from project using task ID."""
        for task in tasks:
            self._client.tasks.delete(task["gid"])

    def update_tasks(self, **tasks):
        """Update tasks with supplied metadata in the project."""
        for task, data in tasks.items():
            self._client.tasks.update(task["gid"], data)


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
