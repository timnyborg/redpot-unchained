from django.utils.html import format_html
import django_tables2 as tables


class PoundsColumn(tables.Column):
    def render(self, value):
        return f'£{value:0.2f}'


class LinkColumn(tables.Column):
    empty_values = ()  # Prevents the table from rendering Nothing, since it's an entirely generated column
    linkify = True  # get_absolute_url

    attrs = {
        'td': {
            'style': 'width: 1px;'  # Must be a better way of making these as narrow as possible
        }
    }

    def __init__(self, verbose_name, **kwargs):
        # Always disable sorting and header.
        # Avoids having to say so every time it's used: view = ViewLinkColumn(orderable=False...)
        kwargs.update({
            'orderable': False,
            'linkify': self.linkify,  # wraps render() in an <a> linking to get_absolute_url()
            'accessor': 'id',  # could be literally anything on the model
            'exclude_from_export': True,
        })
        super().__init__(verbose_name=verbose_name, **kwargs)


class ViewLinkColumn(LinkColumn):
    def render(self, record):
        return format_html('<i class="fas fa-search" title="View"></i>')


class EditLinkColumn(LinkColumn):
    def linkify(self, record):
        return record.get_edit_url()

    def render(self, record):
        return format_html('<i class="fas fa-pencil-alt" title="Edit"></i>')


class DeleteLinkColumn(LinkColumn):
    def linkify(self, record):
        return record.get_delete_url()

    def render(self, record):
        return format_html("""
            <span class="text-danger" title="Delete">
                <i class="fas fa-times"></i>
            </span>
        """)

