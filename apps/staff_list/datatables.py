import django_tables2 as tables

from django.utils.html import format_html

from apps.core.utils.datatables import ViewLinkColumn

from .models import User


class StaffListTable(tables.Table):
    link = ViewLinkColumn('')
    first_name = tables.Column(linkify=True)
    last_name = tables.Column(linkify=True)

    class Meta:
        model = User
        template_name = "django_tables2/bootstrap4.html"
        fields = ('first_name', 'last_name', 'role', 'division', 'email', 'phone_number')

    def render_email(self):
        return format_html("<i class='fas fa-envelope'></i>")
