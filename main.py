"""
Schedule to Google Calendar Script

This script allows users to import or update schedule data from different schools into Google Calendar.
It provides a command-line interface to interact with the user and manage the schedule data.

Author: Tuan Anh Phan

Usage:
    - Run the script, select the school, and choose the mode (Import or Update).
    - For importing and updating, the user needs to provide their username and password for authentication.

Classes:
    - `CalendarHelper`: Helper class for formatting schedule data.
    - `Calendar`: Represents the Google Calendar API interaction.

Functions:
    - `get_user_credentials()`: Prompt the user for their username and password.
    - `get_school()`: Prompt the user to select their school.
    - `get_semester(schedule)`: Prompt the user to select the semester and year.
    - `import_school_module(name)`: Import the school-specific module dynamically.
    - `import_schedule(school)`: Import the schedule data from the selected school.
    - `update_schedule(from_school)`: Update an existing calendar with new schedule data.
    - `main()`: Main function to interact with the user and execute import/update actions.

Usage:
    - Run the script and follow the prompts to import or update schedule data.

Note:
    - The script assumes that school-specific modules are available in the 'schools' directory.
    - Google Calendar API credentials and configurations are not included in this script.
    - Ensure that you have the necessary dependencies installed (e.g., PyInquirer).

"""

import importlib
import pkgutil

import config
from api.calendar_helper import CalendarHelper
from api.gg_calendar import Calendar
from examples import custom_style_3
from PyInquirer import prompt

cal = Calendar()


def get_user_credentials():
    print("Please provide your username and password for authentication")
    questions = [
        {
            "type": "input",
            "name": "username",
            "message": "Username",
        },
        {
            "type": "password",
            "name": "password",
            "message": "Password",
        },
    ]
    answers = prompt(questions, style=custom_style_3)
    return [answers["username"], answers["password"]]


def get_school():
    package = importlib.import_module("schools")
    subpackage_name = []
    for _, name, _ in pkgutil.walk_packages(package.__path__):
        subpackage_name.append(name)

    questions = {
        "type": "list",
        "name": "school",
        "message": "Your school:",
        "choices": [name.upper() for name in subpackage_name],
    }
    answers = prompt(questions, style=custom_style_3)
    return answers["school"].lower()


def get_semester(schedule):
    data = {}
    semesters = schedule.get_semesters()
    questions = []
    for key, value in semesters.items():
        questions.append(
            {
                "type": "list",
                "name": f"{key}",
                "message": f"{key.capitalize()}",
                "choices": value,
            }
        )
    answers = prompt(questions, style=custom_style_3)
    for key in semesters.keys():
        data[key] = answers[key]
    return data


def import_school_module(name: str):
    module = importlib.import_module(f"schools.{name}.schedule")
    schedule_class = getattr(module, f"{name.upper()}Schedule")
    return schedule_class


def import_schedule(school):
    calendar_name = input(f"(Optional) Calendar name (default: {config.DEFAULT_NAME}):")

    if not calendar_name:
        calendar_name = config.DEFAULT_NAME

    if cal.is_exist(calendar_name):
        print("This calendar is already exists.")
        return
    else:
        username, password = get_user_credentials()
        schedule_class = import_school_module(school)
        schedule = schedule_class(username, password)
        try:
            schedule.user.login()
            result = get_semester(schedule)
            if len(result) == 1:
                semester = result["semesters"]
                schedule_data = schedule.get_data(semester=semester)
            else:
                semester = result["semesters"]
                year = result["years"]
                schedule_data = schedule.get_data(semester=semester, year=year)

            schedule_data = CalendarHelper.format(schedule_data)
            cal.create_calendar(calendar_name)
            cal.create_event(schedule_data, calendar_name)
        finally:
            schedule.user.logout()


def update_schedule(from_school):
    calendar_name = input(f"(Optional) Calendar name (default: {config.DEFAULT_NAME}):")

    if not calendar_name:
        calendar_name = config.DEFAULT_NAME

    if cal.is_exist(calendar_name):
        username, password = get_user_credentials()
        schedule = import_school_module(from_school)
        schedule = schedule(username, password)
        try:
            schedule.user.login()
            result = get_semester(schedule)
            if len(result) == 1:
                semester = result["semesters"]
                schedule_data = schedule.get_data(semester=semester)
            else:
                semester = result["semesters"]
                year = result["years"]
                schedule_data = schedule.get_data(semester=semester, year=year)

            schedule_data = CalendarHelper.format(schedule_data)
            cal.delete_calendar(calendar_name)
            cal.create_calendar(calendar_name)
            cal.create_event(schedule_data, calendar_name)
        finally:
            schedule.user.logout()
    else:
        print("This calendar is not exists.")
        return


def main():
    questions = {
        "type": "list",
        "name": "mode",
        "message": "Available options",
        "choices": ["Import", "Update", "Exit"],
    }

    print("SGU Schedule to Google Calendar by Tuan Anh Phan")
    school = get_school()
    options = prompt(questions, style=custom_style_3)
    if options["mode"] == "Import":
        import_schedule(school)
    elif options["mode"] == "Update":
        update_schedule(school)
    elif options["mode"] == "Exit":
        exit()
    else:
        print("This option is not available.")

    input("Press Enter to continue...")


if __name__ == "__main__":
    main()
