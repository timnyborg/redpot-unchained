from pathlib import Path
from typing import Type

from weasyprint import CSS, HTML
from weasyprint.fonts import FontConfiguration

from django import http
from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import ModelForm
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views import generic

from apps.contract import forms, models
from apps.core.utils.strings import normalize
from apps.core.utils.views import AutoTimestampMixin, PageTitleMixin
from apps.tutor.models import TutorModule

from . import services

FORM_MAP = {
    models.Types.CASUAL_TEACHING: forms.CasualTeachingForm,
    models.Types.GUEST_SPEAKER: forms.GuestSpeakerForm,
}


class Create(PermissionRequiredMixin, SuccessMessageMixin, PageTitleMixin, AutoTimestampMixin, generic.CreateView):
    model = models.Contract
    permission_required = 'contract.create_contract'
    template_name = 'contract/form.html'
    success_message = 'Contract created'

    def dispatch(self, request, *args, **kwargs) -> http.HttpResponse:
        self.tutor_module = get_object_or_404(TutorModule, pk=self.kwargs['tutor_module_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self) -> Type[ModelForm]:
        try:
            return FORM_MAP[self.kwargs['type']]
        except KeyError:
            raise http.Http404('Invalid contract type')

    def get_initial(self) -> dict:
        initial = super().get_initial()
        # Currently includes defaults for both contract types, since it's a short, overlapping list
        module = self.tutor_module.module
        if module.portfolio in (17, 32):  # todo: consider alternatives
            initial['payment_preconditions'] = (
                'Payment for marking will be made after you submit the '
                'completed Student Register and Student Assessment forms'
            )
        return {
            **initial,
            'return_to': self.request.user.get_full_name(),
            'email': module.email,
            'phone': module.phone,
            'venue': module.location,
            'start_date': module.start_date,
            'end_date': module.end_date,
        }

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        return {
            **context,
            'student': self.tutor_module.tutor.student,
            'module': self.tutor_module.module,
        }

    def form_valid(self, form) -> http.HttpResponse:
        form.instance.tutor_module = self.tutor_module
        form.instance.type = self.kwargs['type']
        fixed_properties = services.generate_fixed_properties(contract=form.instance)
        form.instance.options = {**fixed_properties, **form.extra_cleaned_data}
        return super().form_valid(form)


class Edit(PermissionRequiredMixin, SuccessMessageMixin, PageTitleMixin, AutoTimestampMixin, generic.UpdateView):
    model = models.Contract
    permission_required = 'contract.change_contract'
    template_name = 'contract/form.html'
    success_message = 'Contract updated'

    def get_form_class(self) -> Type[ModelForm]:
        return FORM_MAP[self.object.type]

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        return {
            **context,
            'student': self.object.tutor_module.tutor.student,
            'module': self.object.tutor_module.module,
        }

    def get_initial(self) -> dict:
        initial = super().get_initial()
        return {**initial, **self.object.options}

    def has_permission(self) -> bool:
        contract = self.get_object()
        return super().has_permission() and contract.is_editable

    def form_valid(self, form) -> http.HttpResponse:
        fixed_properties = services.generate_fixed_properties(contract=form.instance)
        form.instance.options = {**fixed_properties, **form.extra_cleaned_data}
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


class View(PermissionRequiredMixin, PageTitleMixin, generic.DetailView):
    model = models.Contract
    permission_required = 'tutor_contract.view_contract'
    template_name = 'contract/view.html'
    extra_context = {'statuses': models.Statuses}

    def get_subtitle(self) -> str:
        return f"View – {self.object.tutor_module}"
