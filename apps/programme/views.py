from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Subquery, OuterRef
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.detail import DetailView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme

from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView

from apps.core.utils.views import PageTitleMixin
from apps.module.models import ModuleStatus, Module
from .models import Programme, ProgrammeModule
from .forms import ProgrammeEditForm, ProgrammeNewForm, AttachModuleForm
from .datatables import ProgrammeSearchTable, ProgrammeSearchFilter


class View(LoginRequiredMixin, PageTitleMixin, DetailView):
    model = Programme
    template_name = 'programme/view.html'

    def get_context_data(self, **kwargs):
        context = super(View, self).get_context_data(**kwargs)
        programme = self.object

        # Get 100 most recent child modules, with a count of enrolment places taken
        # Subquery to get places_taken per module
        enrolment_count = (
            Module.objects
            .filter(id=OuterRef('id'))
            .filter(enrolments__status__takes_place=True)
            .annotate(count=Count('enrolments__id'))
            .values('count')
        )

        modules = (
            programme.modules
            .annotate(enrolment_count=Subquery(enrolment_count))
            .select_related('status')
            .order_by('-start_date')[:100]
        )

        module_count = programme.modules.count()
        students = programme.qas.select_related('student').order_by('-start_date')[:200]

        module_statuses = ModuleStatus.objects.all()

        return {
            **context,
            'modules': modules,
            'students': students,
            'module_count': module_count,
            'modules_statuses': module_statuses
        }


class Edit(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, UpdateView):
    model = Programme
    form_class = ProgrammeEditForm
    template_name = 'programme/edit.html'
    success_message = 'Details updated.'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user
        })
        return kwargs

    def form_valid(self, form):
        form.instance.modified_on = datetime.now()
        form.instance.modified_by = self.request.user.username
        return super().form_valid(form)


class New(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, CreateView):
    model = Programme
    form_class = ProgrammeNewForm
    template_name = 'programme/edit.html'
    success_message = 'Details updated.'

    def form_valid(self, form):
        # No need to handle created_on or modified_on as they use auto_now_add=True
        form.instance.modified_by = self.request.user.username
        form.instance.created_by = self.request.user.username
        return super().form_valid(form)


class Search(LoginRequiredMixin, PageTitleMixin, SingleTableMixin, FilterView):
    template_name = 'programme/search.html'
    model = Programme
    table_class = ProgrammeSearchTable
    filterset_class = ProgrammeSearchFilter
    subtitle = 'Search'


class AddModule(LoginRequiredMixin, SuccessMessageMixin, PageTitleMixin, CreateView):
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
        return reverse('programme:view', args=[self.object.programme_id])


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


class RemoveModule(LoginRequiredMixin, PageTitleMixin, DeleteView):
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
            module=self.kwargs['module_id']
        )

    def get_success_url(self):
        messages.success(self.request, self.success_message)  # DeleteViews don't do this automatically
        if url_has_allowed_host_and_scheme(self.request.GET.get('next'), allowed_hosts=None):
            return self.request.GET.get('next')
        return self.object.module
