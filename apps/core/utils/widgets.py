"""
Contains:
    * Standardized Date/Datetime/Time widgets that can be used across the application.
      (Allows us to configure just once (e.g. default format), and swap libraries if ever necessary)
    * Standard widgets with bootstrap prepends/appends (e.g. pound sign)

"""
from datetime import datetime
from typing import Type

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

    def __init__(self, model: Type[models.Model], link: bool = False, *args, **kwargs):
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


class ToggleWidget(widgets.CheckboxInput):
    """A checkbox widget using the bootstraptoggle library"""

    base_attrs = {
        'togglewidget': True,  # Hack to override checkbox layout in bootstrap3_form.html.  todo: coherent approach
        'data-toggle': 'toggle',
        'data-on': 'On',
        'data-off': 'Off',
        'data-onstyle': "success",
        'data-offstyle': "warning",
    }

    class Media:
        css = {'all': ('https://cdn.jsdelivr.net/gh/gitbrent/bootstrap4-toggle@3.6.1/css/bootstrap4-toggle.min.css',)}
        js = ('https://cdn.jsdelivr.net/gh/gitbrent/bootstrap4-toggle@3.6.1/js/bootstrap4-toggle.min.js', 'actions.js')

    def __init__(self, attrs=None, check_test=None):
        attrs = {**self.base_attrs, **(attrs or {})}
        super().__init__(attrs, check_test)
        """
        _data-on':'Non-credit', '_data-off':'For credit    ', '_data-offstyle':'success', '_data-onstyle':'warning'}
        """


class DatalistTextInput(widgets.TextInput):
    """Text input with pre-defined selections (a datalist).  Takes a list of options"""

    template_name = 'widgets/datalist_text_input.html'

    def __init__(self, options: list, attrs=None):
        self.options = options
        super().__init__(attrs)

    def get_context(self, name, value, attrs) -> dict:
        context = super().get_context(name, value, attrs)
        context['widget']['attrs']['list'] = f'datalist_{name}'
        context['widget']['options'] = self.options
        return context
