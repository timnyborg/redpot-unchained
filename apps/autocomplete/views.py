from dal import autocomplete

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, QuerySet, Value
from django.db.models.functions import Concat

from apps.core.models import User
from apps.enrolment.models import Enrolment
from apps.module.models import Module
from apps.tutor.models import RightToWorkDocumentType, Tutor, TutorModule


class ModuleAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self) -> QuerySet[Module]:
        qs = Module.objects.all()
        if self.q:
            # Filter on name or code containing the string
            qs = qs.filter(Q(title__unaccent__icontains=self.q) | Q(code__icontains=self.q)).order_by('-id')
        return qs

    def get_result_label(self, result: Module) -> str:
        return result.long_form


class TutorAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self) -> QuerySet[Tutor]:
        qs = Tutor.objects.select_related('student')
        if self.q:
            # Filter on '<first> <last>' or '<nickname> <last>' containing the string
            return (
                qs.annotate(search_name=Concat('student__firstname', Value(' '), 'student__surname'))
                .annotate(search_nickname=Concat('student__nickname', Value(' '), 'student__surname'))
                .filter(Q(search_name__unaccent__icontains=self.q) | Q(search_nickname__unaccent__icontains=self.q))
                .order_by('student__firstname', 'student__surname')
                .prefetch_related('subjects')
            )
        return qs

    def get_result_label(self, result: Tutor) -> str:
        subjects = result.subjects.all()
        if subjects:
            subject_text = ', '.join(map(str, subjects))
            return f'{result.student} ({subject_text})'
        return f'{result.student}'


class EnrolmentAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self) -> QuerySet[Enrolment]:
        qs = Enrolment.objects.select_related('qa__student', 'module')
        if self.q:
            # Filter on name or code containing the string
            qs = qs.filter(
                Q(module__title__unaccent__icontains=self.q) | Q(module__code__icontains=self.q),
            ).order_by('-id', 'qa__student__firstname', 'qa__student__surname')
        return qs

    def get_result_label(self, result: Enrolment) -> str:
        return f'{result.module.code} - {result.qa.student}'


class TutorModuleAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self) -> QuerySet[TutorModule]:
        qs = TutorModule.objects.select_related('tutor__student', 'module')
        if self.q:
            # Filter on name or code containing the string
            qs = qs.filter(
                Q(module__title__unaccent__icontains=self.q) | Q(module__code__icontains=self.q),
            ).order_by('-id', 'tutor__student__firstname', 'tutor__student__surname')
        return qs

    def get_result_label(self, result: TutorModule) -> str:
        return f'{result.module.code} - {result.module.title} - {result.tutor.student}'


class RtwAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self) -> QuerySet[RightToWorkDocumentType]:
        qs = RightToWorkDocumentType.objects.all()

        rtw_type = self.forwarded.get('rtw_type')

        if rtw_type:
            qs = qs.filter(rtw_type=rtw_type)

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class UserAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self) -> QuerySet[User]:
        qs = User.objects.order_by('first_name', 'last_name')
        if self.q:
            qs = qs.filter(Q(first_name__contains=self.q) | Q(last_name__contains=self.q))
        return qs

    def get_result_label(self, result: User) -> str:
        return result.get_full_name()
