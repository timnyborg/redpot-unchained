from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, OuterRef, Subquery
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from apps.core.utils.urls import next_url_if_safe
from apps.core.utils.views import AutoTimestampMixin, DeletionFailedMessageMixin, PageTitleMixin
from apps.module.models import Module, ModuleStatus

from .datatables import ProgrammeSearchFilter, ProgrammeSearchTable
from .forms import AttachModuleForm, ProgrammeEditForm, ProgrammeNewForm
from .models import Programme, ProgrammeModule


class View(LoginRequiredMixin, PageTitleMixin, generic.DetailView):
    model = Programme
    template_name = 'programme/view.html'

    def get_context_data(self, **kwargs):
        context = super(View, self).get_context_data(**kwargs)
        programme = self.object

        # Get 100 most recent child modules, with a count of enrolment places taken
        # Subquery to get places_taken per module
        enrolment_count = (
            Module.objects.filter(id=OuterRef('id'))
            .filter(enrolment__status__takes_place=True)
            .annotate(count=Count('enrolment__id'))
            .values('count')
        )

        modules = (
            programme.modules.annotate(enrolment_count=Subquery(enrolment_count))
            .select_related('status')
            .order_by('-start_date')[:100]
        )

        module_count = programme.modules.count()
        students = programme.qualification_aims.select_related('student').order_by('-start_date')[:200]

        module_statuses = ModuleStatus.objects.all()

        return {
            **context,
            'modules': modules,
            'students': students,
            'module_count': module_count,
            'modules_statuses': module_statuses,
        }


class Edit(LoginRequiredMixin, PageTitleMixin, AutoTimestampMixin, SuccessMessageMixin, generic.UpdateView):
    model = Programme
    form_class = ProgrammeEditForm
    template_name = 'core/form.html'
    success_message = 'Details updated.'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class New(PermissionRequiredMixin, PageTitleMixin, AutoTimestampMixin, SuccessMessageMixin, generic.CreateView):
    model = Programme
    form_class = ProgrammeNewForm
    permission_required = 'programme.add_programme'
    template_name = 'core/form.html'
    success_message = 'Programme created'


class Search(LoginRequiredMixin, PageTitleMixin, SingleTableMixin, FilterView):
    template_name = 'core/search.html'
    queryset = Programme.objects.select_related('portfolio', 'division', 'qualification')
    table_class = ProgrammeSearchTable
    filterset_class = ProgrammeSearchFilter
    subtitle = 'Search'


class Delete(PermissionRequiredMixin, DeletionFailedMessageMixin, PageTitleMixin, generic.DeleteView):
    model = Programme
    permission_required = 'programme.delete_programme'
    template_name = 'core/delete_form.html'
    success_url = reverse_lazy('programme:search')


class AddModule(LoginRequiredMixin, SuccessMessageMixin, PageTitleMixin, generic.CreateView):
    template_name = 'core/form.html'
    model = ProgrammeModule
    form_class = AttachModuleForm
    success_message = 'Module attached'

    def dispatch(self, request, *args, **kwargs):
        """
        Overridden so we can make sure the Programme instance exists
        """
        self.programme = get_object_or_404(Programme, pk=kwargs['programme_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self) -> dict:
        return {'programme': self.programme}

    def get_success_url(self) -> str:
        return self.programme.get_absolute_url()


class RemoveModule(LoginRequiredMixin, PageTitleMixin, generic.DeleteView):
    model = ProgrammeModule
    template_name = 'programme/remove_module.html'
    subtitle = 'Remove'
    subtitle_object = False

    def get_object(self, queryset=None):
        # A special override because I'm calling this class with /programme_id/module_id/ instead of /pk/
        return get_object_or_404(
            ProgrammeModule,
            programme=self.kwargs['programme_id'],
            module=self.kwargs['module_id'],
        )

    def get_success_url(self) -> str:
        messages.success(self.request, f'{self.object.module} removed from {self.object.programme}')
        return next_url_if_safe(self.request) or self.object.get_absolute_url()
