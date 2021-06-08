from dal import autocomplete

from django.db.models import Q

from apps.module.models import Module
from apps.tutor.models import Tutor


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
