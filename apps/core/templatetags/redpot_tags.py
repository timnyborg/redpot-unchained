import socket
from typing import Union

from django import template
from django.core.cache import cache
from django.db.models import Model
from django.utils.safestring import mark_safe

from ..models import User

register = template.Library()


@register.simple_tag
def edit_button(url: Union[str, Model], icon: str = 'pencil-alt', target: str = '', tooltip: str = 'Edit details'):
    """Produces a standard edit button.  Can take a string url, or a Model that implements get_edit_url()"""
    if isinstance(url, Model):
        if hasattr(url, 'get_edit_url'):
            url = url.get_edit_url()
        else:
            raise AttributeError(f'The model {url._meta.object_name} needs to define get_edit_url()')

    button = f"""
        <a href="{url}"
           class="btn btn-default btn-lg pull-right"
           target="{target}"
           data-toggle': 'tooltip'
           title='{tooltip}'
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


@register.inclusion_tag('utility/bootstrap3_form.html')
def bootstrap3form(form, status_classes=True):
    return {'form': form, 'status_classes': status_classes}


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
    return mark_safe(
        f"""
        <button type="submit" class="btn btn-{btn_type}">
            {text}
        </button>'
        """
    )


@register.simple_tag
def bootstrap3delete(url: str, btn_type: str = 'danger', text: str = 'Delete'):
    return mark_safe(
        f"""
        <a href="{url}" class="pull-right btn btn-{btn_type}">
            {text}
        </a>
        """
    )


@register.simple_tag
def bootstrap3backbutton(text='Back', btn_type='default'):
    return mark_safe(
        f"""
        <a class='btn btn-{btn_type}' href="javascript:history.back()">{text}</a>
    """
    )


@register.simple_tag
def watermark(text=socket.gethostname()):
    return mark_safe(
        f"""
        <div id='watermark'>{(text + ' ')*150}</div>
    """
    )
