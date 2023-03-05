# Asana2Calendar

This is a Python-based application that allows you to sync events between tasks in an [Asana](https://asana.com) project and events in a [CalDAV](https://wikipedia.org/wiki/CalDAV) calendar. The application uses [SQLite](https://github.com/sqlite/sqlite) as its database system with [CalDAV](https://github.com/python-caldav/caldav) and [Asana](https://github.com/Asana/python-asana) libraries to access their respective APIs.

## Prerequisites
- Have a project with custom field title, 'Location' and type 'Text'.
- Create your asana client ID by following the instructions [here](https://developers.asana.com/docs/personal-access-token).

## Installation
1. Clone the repository:
```bash
git clone https://github.com/dylantjb/asana2calendar.git
```

2. Install the required Python packages using pip:
```bash
pip install -r requirements.txt
```

## Usage
1. Run the `setup.py` script to create the database:
```bash
python setup.py
```

2. Copy the `config.example.ini` file to your config directory.
```bash
mkdir -p "${XDG_CONFIG_DIR:-$HOME/.config}/asana2calendar"
cp config.example.ini "${XDG_CONFIG_DIR:-$HOME/.config}/asana2calendar/config.ini"
```

3. Run the `main.py` script with your asana client ID to start the application:
```bash
ASANA_CLIENT_ID='123456' python main.py
```

## TODO
- Use OAuth instead of PAT
- Recurring events
- User can choose to dry run sync changes
- Support for Google and Outlook calendars
- Allow to sync as caldav tasks and appointments

## Contributing
It would be greatly appreciated to help tick off some items in the todo section or find bugs and file issues for them.
If you would like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your changes.
3. Make your changes and commit them to the new branch.
4. Push your changes to your forked repository.
5. Submit a pull request.

All python code is formatted with [black](https://github.com/psf/black) and [isort](https://github.com/PyCQA/isort), and linted with [pylint](https://github.com/PyCQA/pylint).

## License
This project is licensed under the GPLv3 License. See the [COPYING](COPYING) for more information.

