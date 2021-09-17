import socket
from typing import Optional, Union

from django import template
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
           class="btn btn-default btn-outline-dark {sizes.get(size, '')} pull-right float-end"
           target="{target}"
           data-toggle="tooltip"
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
def bootstrap5form(form, status_classes=True, input_size='normal'):
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


@register.inclusion_tag('utility/bootstrap3_modal.html')
def bootstrap3modal(
    modal_id, body, confirm_class='primary', confirm_text='Submit', cancel_text='Close', header='Confirm'
):
    """Description from redpot: "A first stab at a terse modal generator".  Guess it stuck?"""
    return {
        'modal_id': modal_id,
        'body': body,
        'confirm_class': confirm_class,
        'confirm_text': confirm_text,
        'cancel_text': cancel_text,
        'header': header,
    }


@register.inclusion_tag('utility/bootstrap4_form.html')
def bootstrap4form(form, status_classes=True):
    return {'form': form, 'status_classes': status_classes}


@register.inclusion_tag('utility/bootstrap4_modal.html')
def bootstrap4modal(
    modal_id, body, confirm_class='primary', confirm_text='Submit', cancel_text='Close', header='Confirm'
):
    """Description from redpot: "A first stab at a terse modal generator".  Guess it stuck?"""
    return {
        'modal_id': modal_id,
        'body': body,
        'confirm_class': confirm_class,
        'confirm_text': confirm_text,
        'cancel_text': cancel_text,
        'header': header,
    }


@register.simple_tag
def bootstrap3submit(text: str = 'Submit', btn_type: str = 'primary'):
    return mark_safe(f"<button type='submit' class='btn btn-{btn_type}'>{text}</button>")


@register.simple_tag
def bootstrap3delete(url: str, btn_type: str = 'danger', text: str = 'Delete'):
    return mark_safe(f"<a href='{url}' class='pull-right btn btn-{btn_type}'>{text}</a>")


@register.simple_tag
def bootstrap3backbutton(text='Back', btn_type='default'):
    return mark_safe(f"<a class='btn btn-{btn_type}' href='javascript:history.back()'>{text}</a>")


@register.simple_tag
def watermark(text: Optional[str] = None):
    if not text:
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
def icon_text(text, icon_type):
    return mark_safe(
        f"""
        <span class="fa {icon_type}"></span> {text}
    """
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
