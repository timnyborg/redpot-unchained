import django_tables2 as tables

from django.urls import reverse

from apps.core.utils.datatables import EditLinkColumn, PoundsColumn

from . import models


class ApprovalTable(tables.Table):
    amendment = tables.CheckBoxColumn(
        accessor='id',
        attrs={"th__input": {"id": "toggle-all"}},
        orderable=False,
    )
    amount = PoundsColumn()
    student = tables.Column('Student', accessor='enrolment__qa__student', linkify=True)
    module = tables.Column('Module', accessor='enrolment__module', linkify=True)
    edit = EditLinkColumn(
        verbose_name='', linkify=lambda record: record.get_edit_url() + f'?next={reverse("amendment:approve")}'
    )

    class Meta:
        model = models.Amendment
        template_name = "django_tables2/bootstrap.html"
        fields = (
            'amendment',
            'type',
            'student',
            'module',
            'amount',
            'requested_by',
            'requested_on',
            'edit',
        )
        per_page = 20
        order_by = ('pk',)
