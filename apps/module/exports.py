from import_export import fields, resources, widgets

from django.db.models import Max, Q

from apps.enrolment.models import Enrolment
from apps.moodle import services as moodle_services
from apps.moodle.models import MoodleID
from apps.student.models import OtherID


class FormattedAddressWidget(widgets.Widget):
    def render(self, value, obj=None):
        return value.replace("\n", " ")


class StudentListExport(resources.ModelResource):
    def export(self, queryset=None, *args, **kwargs):
        # do the extra query annotation here, so the view need only pass in the filtered enrolments queryset
        card = Max('qa__student__other_id__number', filter=Q(qa__student__other_id__type=OtherID.Types.STUDENT_CARD))
        email = Max(
            'qa__student__email__email',
            filter=Q(qa__student__email__is_default=True),
        )
        address = Max(
            'qa__student__address__formatted',
            filter=Q(qa__student__address__is_default=True),
        )
        queryset = queryset.select_related(
            'module', 'qa', 'qa__student', 'qa__student__nationality', 'status'
        ).annotate(card=card, email=email, address=address)
        return super().export(queryset, *args, **kwargs)

    student_title = fields.Field(attribute='qa__student__title', column_name='title')
    first_or_nickname = fields.Field()
    surname = fields.Field(attribute='qa__student__surname')
    email_optin = fields.Field(attribute='qa__student__email_optin')
    nationality = fields.Field(attribute='qa__student__nationality__name')
    status = fields.Field(attribute='status__description')
    card = fields.Field(attribute='card')
    module_title = fields.Field(attribute='module__title')
    module_code = fields.Field(attribute='module__code')
    email = fields.Field(attribute='email')
    phone_numbers = fields.Field()
    address = fields.Field(attribute='address', widget=FormattedAddressWidget())

    def dehydrate_first_or_nickname(self, enrolment: Enrolment):
        return enrolment.qa.student.first_or_nickname

    def dehydrate_phone_numbers(self, enrolment: Enrolment):
        return ', '.join(map(str, enrolment.qa.student.phones.all()))


class ConstantField(fields.Field):
    """
    A simple field to output the same value on every row:
        myfield = ConstantField('myvalue')
    """

    def __init__(self, value=None, *args, **kwargs):
        self.value = value
        super().__init__(*args, **kwargs)

    def export(self, obj):
        return self.value


class MoodleListExport(resources.ModelResource):
    def export(self, queryset=None, *args, **kwargs):
        # do the extra query annotation here, so the view need only pass in the filtered enrolments queryset
        email = Max(
            'qa__student__email__email',
            filter=Q(qa__student__email__is_default=True),
        )
        queryset = queryset.select_related('module', 'qa', 'qa__student', 'qa__student__moodle_id', 'status').annotate(
            email=email
        )
        return super().export(queryset, *args, **kwargs)

    # For moodle import template
    username = fields.Field(attribute='qa__student__moodle_id__moodle_id')
    password = fields.Field()
    firstname = fields.Field(attribute='qa__student__firstname')
    lastname = fields.Field(attribute='qa__student__surname')
    email = fields.Field(attribute='email')
    maildisplay = ConstantField(0)
    autosubscribe = ConstantField(0)
    profile_field_courseids = fields.Field(attribute='module__code')
    # For admin use
    paid = fields.Field(column_name='Paid?')
    status = fields.Field(attribute='status__description')
    course_title = fields.Field(attribute='module__title')

    def dehydrate_password(self, enrolment: Enrolment) -> str:
        try:
            moodle_id = enrolment.qa.student.moodle_id
            if moodle_id.first_module_code == enrolment.module.code:
                return moodle_services.get_random_string()
            return 'the same as before'
        except MoodleID.DoesNotExist:
            return ''

    def dehydrate_paid(self, enrolment: Enrolment) -> str:
        return 'No' if enrolment.get_balance() else 'Yes'
