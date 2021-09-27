from datetime import datetime
from pathlib import Path

from weasyprint import CSS, HTML
from weasyprint.fonts import FontConfiguration

from django import http
from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views import generic

from apps.contract import forms, models
from apps.core.utils.postal import FormattedAddress
from apps.core.utils.strings import normalize
from apps.core.utils.views import AutoTimestampMixin, PageTitleMixin
from apps.tutor.models import RightToWorkType


class Edit(PermissionRequiredMixin, SuccessMessageMixin, PageTitleMixin, AutoTimestampMixin, generic.UpdateView):
    model = models.Contract
    permission_required = 'contract.change_contract'
    template_name = 'contract/edit.html'
    success_message = 'Contract updated'

    def get_form_class(self):
        mapping = {
            models.Types.CASUAL_TEACHING: forms.CasualTeachingForm,
            models.Types.GUEST_SPEAKER: forms.GuestSpeakerForm,
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
            'full_name': f"{student.title or ''} {student.firstname} {student.surname}",
            'salutation': f"{student.title or student.firstname} {student.surname}",
            'doc_date': datetime.today(),
            'address': FormattedAddress(address).as_list(),
            'module': {'title': module.title, 'code': module.code},
            'list_a_rtw': tutor.rtw_type == RightToWorkType.PERMANENT,
            'overseas_rtw': tutor.rtw_type == RightToWorkType.OVERSEAS,
        }
        # Filter form vars to exclude columns from the database rows
        option_vars = form.extra_cleaned_data
        self.object.options = {**fixed_vars, **option_vars}
        return super().form_valid(form)


class PDF(PermissionRequiredMixin, generic.View):
    permission_required = 'tutor_contract.view_contract'

    def get(self, request, pk: int, *args, **kwargs) -> http.HttpResponse:
        contract = get_object_or_404(models.Contract, pk=pk)

        module_code = contract.tutor_module.module.code
        surname = normalize(contract.tutor_module.tutor.student.surname)
        context = {
            **contract.options,
            'status': contract.status,
            'identifier': f'{module_code}-{surname.upper()}-{contract.id}',
            'preview_class': '' if contract.is_signed else 'highlight',
            # todo: handling signatory and signature_image
        }

        template_map = {
            models.Types.CASUAL_TEACHING: 'contract/pdfs/casual_teaching_contract.html',
            models.Types.GUEST_SPEAKER: 'contract/pdfs/guest_speaker_letter.html',
        }
        view = template_map[contract.type]
        html_doc = render_to_string(view, context)

        font_config = FontConfiguration()  # Makes @font-face and google fonts @import work

        output = HTML(
            string=html_doc,
            # Used fetch static images.  Could be done with system file paths, but this'll work for HTML or PDF
            base_url=settings.CANONICAL_URL,
        ).write_pdf(
            stylesheets=[CSS(Path(__file__).parent / 'static/css/tutor_contract.css', font_config=font_config)],
            font_config=font_config,
        )
        filename = normalize(f"contract_{context['full_name']}_{module_code}.pdf")
        return http.HttpResponse(
            output, content_type='application/pdf', headers={'Content-Disposition': f'filename="{filename}"'}
        )
