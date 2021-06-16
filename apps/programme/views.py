from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, OuterRef, Subquery
from django.shortcuts import get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import generic

from apps.core.utils.views import AutoTimestampMixin, PageTitleMixin
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
    template_name = 'programme/edit.html'
    success_message = 'Details updated.'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class New(LoginRequiredMixin, PageTitleMixin, AutoTimestampMixin, SuccessMessageMixin, generic.CreateView):
    model = Programme
    form_class = ProgrammeNewForm
    template_name = 'programme/edit.html'
    success_message = 'Details updated.'


class Search(LoginRequiredMixin, PageTitleMixin, SingleTableMixin, FilterView):
    template_name = 'programme/search.html'
    queryset = Programme.objects.select_related('portfolio', 'division', 'qualification')
    table_class = ProgrammeSearchTable
    filterset_class = ProgrammeSearchFilter
    subtitle = 'Search'


class AddModule(LoginRequiredMixin, SuccessMessageMixin, PageTitleMixin, generic.CreateView):
    template_name = 'programme/add_module.html'
    model = ProgrammeModule
    form_class = AttachModuleForm
    success_message = 'Module attached'

    def dispatch(self, request, *args, **kwargs):
        """
        Overridden so we can make sure the Programme instance exists
        """
        self.programme = get_object_or_404(Programme, pk=kwargs['programme_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Overridden to add the programme
        """
        form.instance.programme = self.programme
        return super().form_valid(form)

    def get_success_url(self):
        return self.programme.get_absolute_url()


# @login_required
# def remove_module(request, programme_id, module_id):
#     try:
#         programme = Programme.objects.get(id=programme_id)
#         module = Module.objects.get(id=module_id)
#     except (Programme.DoesNotExist, Module.DoesNotExist):
#         raise Http404
#
#     # programme.modules.remove(module)
#     messages.success(request, 'Module removed from programme')
#
#     # Example of a safe 'next' redirect (checked against an empty host list to prevent open redirect vulnerability)
#     # could be wrapped into a helper function (safe_next_redirect, which takes next and a fallback if null
#       or invalid)
#     if url_has_allowed_host_and_scheme(request.GET.get('next'), allowed_hosts=None):
#         return redirect(request.GET.get('next'))
#     return redirect(module)


class RemoveModule(LoginRequiredMixin, PageTitleMixin, generic.DeleteView):
    model = ProgrammeModule
    template_name = 'programme/remove_module.html'
    subtitle = 'Remove'
    subtitle_object = False
    success_message = 'Module removed from programme'

    def get_object(self, queryset=None):
        # A special override because I'm calling this class with /programme_id/module_id/ instead of /pk/
        # use get_object_or_404
        return get_object_or_404(
            ProgrammeModule,
            programme=self.kwargs['programme_id'],
            module=self.kwargs['module_id'],
        )

    def get_success_url(self):
        messages.success(self.request, self.success_message)  # DeleteViews don't do this automatically
        if url_has_allowed_host_and_scheme(self.request.GET.get('next'), allowed_hosts=None):
            return self.request.GET.get('next')
        return self.object.module
