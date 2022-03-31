import socket
from typing import Union
from urllib import parse

from django import template
from django.conf import settings
from django.core.cache import cache
from django.db.models import Model
from django.utils.safestring import mark_safe

from ..models import User

register = template.Library()


@register.simple_tag
def edit_button(
    url: Union[str, Model],
    icon: str = 'pencil-alt',
    target: str = '',
    tooltip: str = 'Edit details',
    size: str = 'large',
):
    """Produces a standard edit button.  Can take a string url, or a Model that implements get_edit_url()"""
    if isinstance(url, Model):
        if hasattr(url, 'get_edit_url'):
            url = url.get_edit_url()
        else:
            raise AttributeError(f'The model {url._meta.object_name} needs to define get_edit_url()')

    sizes = {
        'large': 'btn-lg',
        'small': 'btn-sm',
        'medium': '',
    }

    button = f"""
        <a href="{url}"
           class="btn btn-outline-dark {sizes.get(size, '')} float-end"
           target="{target}"
           data-bs-toggle="tooltip"
           title="{tooltip}"
        ><span class='fas fa-{icon}'></span>
        </a>
    """
    return mark_safe(button)


@register.inclusion_tag('utility/timestamp.html')
def timestamp(record):
    return {'record': record}


@register.filter
def user_name(username):
    def _get_name(_username):
        try:
            _instance = User.objects.get(username=_username)
            return _instance.get_full_name()
        except User.DoesNotExist:
            return _username

    return cache.get_or_set(f'user_name_{username}', lambda: _get_name(username))


@register.inclusion_tag('utility/bootstrap_form.html')
def bootstrap_form(form, status_classes=True, input_size='normal'):
    form_control_classes = {
        'normal': "form-control",
        'small': "form-control form-control-sm",
        'large': "form-control form-control-lg",
    }
    form_label_classes = {
        'normal': "col-form-label",
        'small': "col-form-label col-form-label-sm",
        'large': "col-form-label col-form-label-lg",
    }
    return {
        'form': form,
        'status_classes': status_classes,
        'form_control_class': form_control_classes.get(input_size, "form-control"),
        'form_label_class': form_label_classes.get(input_size, "form-label"),
    }


@register.simple_tag
def bootstrap_submit(text: str = 'Submit', btn_type: str = 'primary'):
    return mark_safe(f"<button type='submit' class='btn btn-{btn_type}'>{text}</button>")


@register.simple_tag
def watermark():
    text = settings.WATERMARK
    if not text and settings.DEBUG:
        text = socket.gethostname()
    return mark_safe(f"<div id='watermark'>{(text + ' ')*150}</div>")


@register.simple_tag
def enrolment_label(enrolment_status_id, text):
    enrolment_label_class = {
        # Confirmed
        10: 'text-success',
        11: 'text-success',
        90: 'text-success',
        # Provisional
        20: 'text-default',
        # Withdrawn, deferred
        70: 'text-danger',
        71: 'text-danger',
        76: 'text-danger',
        77: 'text-danger',
        # Transferred
        75: 'text-warning',
    }
    return mark_safe(
        f"<span class='bordered {enrolment_label_class.get(enrolment_status_id)} text-default'>{text}</span>"
    )


@register.simple_tag
def message_icon_class(level_tag):
    """Converts the level_tag of a message to a font-awesome icon class"""
    icon_map = {
        'success': 'fa-check-circle',
        'danger': 'fa-exclamation-triangle',
        'warning': 'fa-exclamation-circle',
        'info': 'fa-info-circle',
    }
    return f"fas fa-fw {icon_map.get(level_tag, 'fa-info-circle')}"


@register.filter
def mul(value, arg):
    return value * arg


@register.filter
def duration(seconds: int) -> str:
    """Format a given number of seconds into days, hours, or minutes"""
    days = seconds // (3600 * 24)
    hours = (seconds % (3600 * 24)) // 3600
    minutes = round((seconds % 3600) / 60)
    if days:
        return f'{days} days'
    elif hours:
        return f'{hours} hours'
    return f'{minutes} minutes'


@register.simple_tag
def square_url(*args, **kwargs) -> str:
    """Generates a link to a Square report
     args: the path of the report
     kwargs: any querystring data that needs to be included

    Example usage: {% square_url 'Folder' 'Subfolder' 'Report name' module=123 %}
    """
    # todo: use a table with report names and urls (relative or absolute?)
    #  so the report paths can be abstracted out of the system
    querystring = parse.urlencode(kwargs)
    path = parse.quote('/'.join(args))
    return mark_safe(settings.SQUARE_URL + f'/report/{path}?{querystring}')
