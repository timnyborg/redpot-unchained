import django_tables2 as tables

from django.utils.html import format_html

from apps.core.utils.datatables import ViewLinkColumn

from .models import User


class StaffListTable(tables.Table):
    link = ViewLinkColumn('')
    first_name = tables.Column(linkify=True)
    last_name = tables.Column(linkify=True)
    short_phone = tables.Column('Phone', accessor='short_phone', order_by='phone')

    class Meta:
        model = User
        template_name = "django_tables2/bootstrap4.html"
        fields = ('first_name', 'last_name', 'role', 'division', 'email', 'short_phone')
        order_by = ('last_name', 'first_name')

    def render_email(self):
        return format_html("<i class='fas fa-envelope'></i>")
