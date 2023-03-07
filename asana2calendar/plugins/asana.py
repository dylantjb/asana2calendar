"""Fetch tasks from project and creates an event in respective caldav calendar."""
from datetime import datetime
from types import SimpleNamespace

from asana import Client


class AsanaEvent(SimpleNamespace):
    data = ["gid", "name", "location", "completed", "due_on", "start_on", "modified_on"]

    def get_data(self):
        return {
            "gid": self.gid,
            "name": self.name,
            "due_on": self.due_on,
            "start_on": self.start_on,
            "modified_on": self.modified_on,
            "completed": self.completed,
        }

    @property
    def due_on(self):
        return datetime.strptime(self.due_on, "%Y-%m-%dT%H:%M:%S.%fZ")

    @due_on.setter
    def due_on(self, due_on):
        self.due_on = due_on.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @property
    def start_on(self):
        return datetime.strptime(self.start_on, "%Y-%m-%dT%H:%M:%S.%fZ")

    @start_on.setter
    def start_on(self, start_on):
        self.start_on = start_on.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @property
    def modified_on(self):
        return datetime.strptime(self.modified_on, "%Y-%m-%dT%H:%M:%S.%fZ")

    @modified_on.setter
    def modified_on(self, modified_on):
        self.modified_on = modified_on.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class AsanaCalendar:  # pylint: disable=no-member
    """An asana project with tasks that represents a calendar with events."""

    def __init__(self, token, name):
        self._client = Client.access_token(token)
        self._client.headers = {"asana-enable": "new_memberships"}
        self._project_id = self.get_project_id(name)

    def get_project_id(self, name):
        """Obtains all projects owned by user and finds the associated ID, using name as a filter.

        Returns associated asana project ID.
        """
        projects = self._client.projects.get_projects(  # type: ignore
            offset=None, iterator_type=None, opt_fields=["name"]
        )  # Paginator disabled without a workspace ID
        return [p for p in projects if p["name"] == name][0]["gid"]

    def get_events(self):
        """Obtains all henceforth tasks associated with the project.
        Retrieves other useful fields.

        Returns AsanaTask objects representing asana events.
        """
        return [
            AsanaEvent(**task)
            for task in self._client.tasks.get_tasks_for_project(  # type: ignore
                self._project_id,
                opt_fields=AsanaEvent.data
                + [
                    "sort_by=due_date",
                    f"due_on.after={datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')}",
                ],
            )
        ]

    def create_events(self, *events):
        """Creates asana tasks from events with supplied metadata in the project."""
        for event in events:
            self._client.tasks.create_task(  # type: ignore
                event.get_data() | {"projects": self._project_id}
            )

    def delete_events(self, *events):
        """Delete asana tasks from project using task ID."""
        for event in events:
            self._client.tasks.delete(event.id)  # type: ignore

    def update_events(self, *events):
        """Update asana tasks with supplied metadata in the project."""
        for event in events:
            self._client.tasks.update(event.id, event.get_data())  # type: ignore
