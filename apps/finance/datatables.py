import django_tables2 as tables

from apps.core.utils.datatables import PoundsColumn
from apps.enrolment.models import Enrolment
from apps.fee.models import Fee


class AddFeesTable(tables.Table):
    fee = tables.CheckBoxColumn(
        accessor='id',
        attrs={"th__input": {"id": "toggle-all"}},
        orderable=False,
    )
    amount = PoundsColumn()
    limit = tables.Column(verbose_name='Shared places left', linkify=True, orderable=False)
    places_left = tables.Column(verbose_name='Places left', empty_values=[], orderable=False)

    def render_limit(self, value):
        return value.places_left()

    def render_places_left(self, record):
        if record.is_single_accom:
            return record.module.get_singles_left()
        elif record.is_twin_accom:
            return record.module.get_twins_left()
        elif record.is_catering:
            if record.allocation and record.allocation > 0:
                return record.allocation - record.catering_booking_count()
            return '∞'  # allocation=0 is unlimited
        return '—'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Places and shared places columns appear only if there's data for any row
        self.columns['limit'].column.visible = any(fee.limit for fee in self.data)
        self.columns['places_left'].column.visible = any(
            fee.is_single_accom or fee.is_twin_accom or fee.is_catering for fee in self.data
        )

    class Meta:
        model = Fee
        template_name = "django_tables2/bootstrap.html"
        fields = ('fee', 'description', 'type', 'amount', 'limit', 'places_left')
        order_by = ('type', 'description')


class OutstandingEnrolmentsTable(tables.Table):
    """Lists a series of enrolments with their outstanding balance (for paying multiple at once)"""

    enrolment = tables.CheckBoxColumn(
        accessor='id',
        attrs={"th__input": {"id": "toggle-all"}},
        orderable=False,
    )
    balance = PoundsColumn()

    class Meta:
        model = Enrolment
        template_name = "django_tables2/bootstrap.html"
        fields = (
            'enrolment',
            'qa__student__surname',
            'qa__student__firstname',
            'module__code',
            'module__title',
            'balance',
        )
        order_by = ('-created_on',)
        per_page = 20
