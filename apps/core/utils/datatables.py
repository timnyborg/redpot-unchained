import django_tables2 as tables

from django.utils.html import format_html


class PoundsColumn(tables.Column):
    def render(self, value):
        return f'£{value:0.2f}'


class LinkColumn(tables.Column):
    empty_values = ()  # Prevents the table from rendering Nothing, since it's an entirely generated column
    linkify = True  # get_absolute_url

    attrs = {'td': {'style': 'width: 1px;'}}  # Must be a better way of making these as narrow as possible
    icon = 'search'
    title = 'View'
    text_class = ''

    def __init__(self, verbose_name, icon=None, title=None, linkify=None, text_class=None, **kwargs):
        # Always disable sorting and header.
        # Avoids having to say so every time it's used: view = ViewLinkColumn(orderable=False...)
        kwargs.update(
            {
                'orderable': False,
                'linkify': linkify or self.linkify,  # wraps render() in an <a> linking to get_absolute_url()
                'accessor': 'id',  # could be literally anything on the model
                'exclude_from_export': True,
            }
        )

        # Allow overriding of properties
        self.title = title or self.title
        self.icon = icon or self.icon
        self.text_class = text_class or self.text_class

        super().__init__(verbose_name=verbose_name, **kwargs)

    def render(self, record):
        return format_html(
            f'''
            <span title="{self.title}" class="{self.text_class}"
               data-bs-toggle="tooltip"
               data-bs-placement="top"
            >
                <i class="fas fa-{self.icon}"></i>
            </span>
            '''
        )


class ViewLinkColumn(LinkColumn):
    icon = 'search'
    title = 'View'


class EditLinkColumn(LinkColumn):
    icon = 'pencil-alt'
    title = 'Edit'

    def linkify(self, record):
        return record.get_edit_url()


class DeleteLinkColumn(LinkColumn):
    icon = 'times'
    title = 'Delete'
    text_class = 'text-danger'

    def linkify(self, record):
        return record.get_delete_url()
