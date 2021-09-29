from dal import autocomplete

from django.db.models import Q

from apps.enrolment.models import Enrolment
from apps.module.models import Module
from apps.tutor.models import RightToWorkDocumentType, Tutor


class ModuleAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Module.objects.all()
        if self.q:
            # Filter on name or code containing the string
            qs = qs.filter(Q(title__unaccent__icontains=self.q) | Q(code__icontains=self.q)).order_by('-id')
        return qs

    def get_result_label(self, result):
        return result.long_form


class TutorAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Tutor.objects.select_related('student')
        if self.q:
            # Filter on name or code containing the string
            qs = qs.filter(
                Q(student__firstname__unaccent__icontains=self.q) | Q(student__surname__icontains=self.q)
            ).order_by('student__firstname', 'student__surname')
        return qs


class EnrolmentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Enrolment.objects.select_related('qa__student', 'module')
        if self.q:
            # Filter on name or code containing the string
            qs = qs.filter(
                Q(module__title__unaccent__icontains=self.q) | Q(module__code__icontains=self.q),
            ).order_by('-id', 'qa__student__firstname', 'qa__student__surname')
        return qs

    def get_result_label(self, result):
        return f'{result.module.code} - {result.qa.student}'


class RtwAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return RightToWorkDocumentType.objects.none()

        qs = RightToWorkDocumentType.objects.all()

        rtw_type = self.forwarded.get('rtw_type', None)

        if rtw_type:
            qs = qs.filter(rtw_type=rtw_type)

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs
