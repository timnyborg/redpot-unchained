"""
Contains:
    * Standardized Date/Datetime/Time widgets that can be used across the application.
      (Allows us to configure just once (e.g. default format), and swap libraries if ever necessary)
    * Standard widgets with bootstrap prepends/appends (e.g. pound sign)

"""

from datetime import datetime

import bootstrap_datepicker_plus

from django.conf import settings
from django.forms import widgets


class PickerOptionsMixin:
    """Remove the extra options by default from our date/time pickers"""

    _default_options = {
        'showClose': False,
        'showClear': False,
        'showTodayButton': False,
    }


class DateTimePickerInput(PickerOptionsMixin, bootstrap_datepicker_plus.DateTimePickerInput):
    format: str = settings.DATETIME_INPUT_FORMATS[0]
    options = {'useCurrent': 'day'}  # Defaults to 00:00 rather than the current time


class DatePickerInput(PickerOptionsMixin, bootstrap_datepicker_plus.DatePickerInput):
    format: str = settings.DATE_INPUT_FORMATS[0]


class MonthPickerInput(PickerOptionsMixin, bootstrap_datepicker_plus.DatePickerInput):
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


class PoundInput(widgets.NumberInput):
    """Bootstrap text input with a £ appended"""

    template_name = "widgets/pound_widget.html"
