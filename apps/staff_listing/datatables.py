import django_tables2 as tables
from .models import User
from apps.core.utils.datatables import ViewLinkColumn
from django.utils.html import format_html

class StaffListTable(tables.Table):
    link = ViewLinkColumn('')
    first_name = tables.Column(linkify=True)
    last_name = tables.Column(linkify=True)
    class Meta:
        model = User
        template_name = "django_tables2/bootstrap.html"
        fields = ('first_name', 'last_name', 'role', 'division', 'email', 'phone_number')

    def render_email(self, value):
        return format_html("<i class='fas fa-envelope'></i>")

