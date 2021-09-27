from datetime import datetime

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic

from apps.contract import forms, models
from apps.core.utils.postal import FormattedAddress
from apps.core.utils.views import AutoTimestampMixin, PageTitleMixin
from apps.tutor.models import RightToWorkType


class Edit(PermissionRequiredMixin, PageTitleMixin, AutoTimestampMixin, generic.UpdateView):
    model = models.Contract
    permission_required = 'contract.change_contract'
    template_name = 'contract/edit.html'

    def get_form_class(self):
        mapping = {
            models.Types.CASUAL_TEACHING: forms.CasualTeachingForm,
            # models.Types.GUEST_SPEAKER: forms.GuestSpeakerForm,
        }
        return mapping[self.object.type]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return {
            **context,
            'student': self.object.tutor_module.tutor.student,
            'module': self.object.tutor_module.module,
        }

    def get_initial(self):
        initial = super().get_initial()
        return {**initial, **self.object.options}

    def has_permission(self):
        contract = self.get_object()
        return super().has_permission() and contract.is_editable

    def form_valid(self, form):
        tutor = self.object.tutor_module.tutor
        student = tutor.student
        module = self.object.tutor_module.module
        address = student.get_default_address()

        # Automatically generated contract properties.  Contract-type-specific vars can be appended later if required
        fixed_vars = {
            'address': FormattedAddress(address).as_list(),
            'module': {'title': module.title, 'code': module.code},
            'list_a_rtw': tutor.rtw_type == RightToWorkType.PERMANENT,
            'list_overseas_rtw': tutor.rtw_type == RightToWorkType.OVERSEAS,
        }

        # Filter form vars to exclude columns from the database rows
        option_vars = form.extra_cleaned_data
        self.object.options = {
            'full_name': f"{student.title or ''} {student.firstname} {student.surname}",
            'salutation': f"{student.title or student.firstname} {student.surname}",
            'doc_date': datetime.today(),
            **fixed_vars,
            **option_vars,
        }
        return super().form_valid(form)
