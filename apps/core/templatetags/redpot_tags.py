import socket

from django import template
from django.core.cache import cache
from django.utils.safestring import mark_safe

from ..models import User

register = template.Library()


@register.simple_tag
def edit_button(url, icon='pencil-alt', target='', tooltip='Edit details'):
    """Produces a standard edit button"""
    b = f"""
        <a href="{url}"
           class="btn btn-default btn-lg pull-right"
           target="{target}"
           data-toggle': 'tooltip'
           title='{tooltip}'
        ><span class='fas fa-{icon}'></span>
        </a>
    """
    return mark_safe(b)


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


@register.inclusion_tag('utility/bootstrap4_form.html')
def bootstrap3form(form, status_classes=True):
    return {'form': form, 'status_classes': status_classes}


@register.inclusion_tag('utility/bootstrap4_modal.html')
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


@register.simple_tag
def bootstrap3submit(text='Submit', btn_type='primary', offset=2):
    return mark_safe(
        f"""
        <div class="form-group">
            <div class="col-sm-offset-{offset} col-sm-{12-offset}">
                <button type="submit" class="btn btn-{btn_type}">{text}</button>
            </div>
        </div>
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
