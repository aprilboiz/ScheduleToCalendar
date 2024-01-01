from datetime import datetime
from math import floor
from typing import List, Dict
from exceptions import ScheduleException


class CalendarHelper:
    """
    Helper class for formatting calendar event data.

    Static Methods:
        format(subjects_data: List[Dict[str, str]]) -> List[Dict[str, str]]:
            Format the input list of subjects data.
    """

    @staticmethod
    def format(subjects_data: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Format the input list of subjects data.

        Args:
            subjects_data (List[Dict[str, str]]): A list of dictionaries containing subject data.

        Returns:
            List[Dict[str, str]]: The formatted list of subjects data with added fields such as
            'repeat', 'start_period_date', 'end_period_date', and 'color'.
        """
        required_keys = ["name", "room"]
        necessary_keys = ["code", "class", "lecturer"]

        subject_colors: Dict[str, str] = {}

        for subject in subjects_data:
            for key in required_keys:
                if key not in subject.keys():
                    raise ScheduleException(f"Missing '{key}' field.")

            for key in necessary_keys:
                if key not in subject.keys():
                    print(f"Warning: Missing '{key}' field of '{subject['name']}'. This field will be blank.")
                    subject[key] = ""

            from_date = datetime.fromisoformat(subject["from_date"])
            to_date = datetime.fromisoformat(subject["to_date"])

            # Calculate the number of weeks between from_date and to_date and convert to string
            subject["repeat"] = str(floor((to_date - from_date).days / 7))
            subject["start_period_date"] = subject["from_date"]

            # Create a datetime object with the same date as from_date and the time from to_date
            subject["end_period_date"] = datetime(
                from_date.year,
                from_date.month,
                from_date.day,
                to_date.hour,
                to_date.minute,
                to_date.second,
            ).isoformat()

            # Assign a color to the subject if it doesn't have one already
            if not subject_colors.get(subject["name"]):
                subject_colors[subject["name"]] = str(len(subject_colors) + 1)

            subject["color"] = subject_colors[subject["name"]]

        return subjects_data
