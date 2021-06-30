"""
Date inputs

Contains standardized Date/Datetime/Time widgets that can be used across the application.
Allows us to configure just once (e.g. default format), and swap libraries if ever necessary
"""

from datetime import datetime

import bootstrap_datepicker_plus

from django.conf import settings


class BaseDatePicker(bootstrap_datepicker_plus.DatePickerInput):
    """Remove the extra options by default from our date/time pickers"""

    _default_options = {
        'showClose': False,
        'showClear': False,
        'showTodayButton': False,
    }


class DatePickerInput(BaseDatePicker):
    format: str = settings.DATE_INPUT_FORMATS[0]


class MonthPickerInput(BaseDatePicker):
    format: str = '%B %Y'

    def value_from_datadict(self, data, files, name):
        """
        Translates a submitted value (e.g. January 2021) into a valid datetime: datetime(2021, 1, 1, 0, 0)
        If the submitted value is invalid, it passes it along unchanged for validation to reject
        """
        value = data.get(name)
        try:
            return datetime.strptime(value, self.format).date()
        except (ValueError, TypeError):
            return value
