# Asana2Calendar

This is a Python-based application that allows you to sync events between tasks in an [Asana](https://asana.com) project and events in a [CalDAV](https://wikipedia.org/wiki/CalDAV) calendar. The application uses [SQLite](https://github.com/sqlite/sqlite) as its database system with [CalDAV](https://github.com/python-caldav/caldav) and [Asana](https://github.com/Asana/python-asana) libraries to access their respective APIs.

## Prerequisites
- Have a project with custom field title, 'Location' and type 'Text'.
- Create your asana client ID by following the instructions [here](https://developers.asana.com/docs/personal-access-token).

## Installation
1. Install the package with pip:
```bash
pip install asana2calendar
```

2. Create your configuration using [config.example.ini] or with:
```bash
asana2calendar --create-config [CONFIG_PATH]
```

3. Create your database with:
```bash
asana2calendar --create-db [DB_PATH]
```

4. Run the package:
```bash
asana2calendar [-c [CONFIG_PATH]] [-d [DB_PATH]]
```

## TODO
- Use OAuth instead of PAT
- Automatic conflict resolution based on the modified_date field.
- Recurring events
- User can choose to dry run sync changes
- Daemon to listen for changes
- Support for Google and Outlook calendars
- Allow to sync as caldav tasks and appointments

## License
This project is licensed under the GPLv3 License. See [LICENSE.txt](LICENSE.txt) for more information.
