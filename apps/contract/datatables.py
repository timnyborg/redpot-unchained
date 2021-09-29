import django_tables2 as tables

from apps.contract import models
from apps.core.utils.datatables import ViewLinkColumn


class ApproveTable(tables.Table):
    contract = tables.CheckBoxColumn(accessor='id', attrs={"th__input": {"id": "toggle-all"}}, orderable=False)
    view = ViewLinkColumn(verbose_name='', attrs={'a': {'target': '_blank'}})

    class Meta:
        model = models.Contract
        fields = [
            'contract',
            'tutor_module__tutor__student__surname',
            'tutor_module__tutor__student__firstname',
            'tutor_module__module__code',
            'tutor_module__module__title',
            'tutor_module__module__start_date',
            'tutor_module__module__end_date',
            'view',
        ]
