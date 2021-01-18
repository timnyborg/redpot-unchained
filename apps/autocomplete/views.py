from django.db.models import Q
from dal import autocomplete

from apps.module.models import Module


class ModuleAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Module.objects.all()

        if self.q:
            # Filter on name or code containing the string
            qs = qs.filter(Q(title__unaccent__icontains=self.q) | Q(code__icontains=self.q)).order_by('-id')

        return qs

    def get_result_label(self, result):
        return result.long_form
