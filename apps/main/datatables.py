from django.utils.html import format_html
import django_tables2 as tables


class PoundsColumn(tables.Column):
    def render(self, value):
        return f'£{value:0.2f}'


class ViewLinkColumn(tables.Column):
    empty_values = ()  # Prevents the table from rendering Nothing, since it's an entirely generated column

    def render(self, record):
        return format_html('<span class="fas fa-search" alt="View"></span>')

    def __init__(self, verbose_name, **kwargs):
        # Always disable sorting and header.
        # Avoids having to say so every time it's used: view = ViewLinkColumn(orderable=False...)
        kwargs.update({
            'orderable': False,
            'linkify': True,  # wraps render() in an <a> linking to get_absolute_url()
            'accessor': 'id',  # could be literally anything on the
            'exclude_from_export': True,
        })
        super(ViewLinkColumn, self).__init__(verbose_name=verbose_name, **kwargs)