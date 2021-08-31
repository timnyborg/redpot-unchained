"""
Contains:
    * Standardized Date/Datetime/Time widgets that can be used across the application.
      (Allows us to configure just once (e.g. default format), and swap libraries if ever necessary)
    * Standard widgets with bootstrap prepends/appends (e.g. pound sign)

"""

from datetime import datetime

import bootstrap_datepicker_plus

from django.conf import settings
from django.db import models
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


class ReadOnlyModelWidget(widgets.Widget):
    """A readonly widget for displaying a single model with bootstrap styling
    Ensure the formfield has `disabled=True`, or you may see errors when posting null data in testing
    If `link=True`, the text will be a hyperlink to the instance's get_absolute_url()
    """

    def __init__(self, model: models.Model, link: bool = False, *args, **kwargs):
        self.model = model
        self.link = link
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None) -> str:
        instance = self.model.objects.get(pk=value)
        # -static for b2, -plaintext for bs4.  todo: consider how to move that into the form rendering
        if self.link:
            text = f'<a href="{instance.get_absolute_url()}">{instance}</a>'
        else:
            text = str(instance)
        return f"""
            <input type="hidden" name="{name}" value="{value}">
            <div class='form-control-static form-control-plaintext'>{text}</div>
        """
