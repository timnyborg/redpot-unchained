from __future__ import annotations

import django_tables2 as tables

from django import http
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Model
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic

from apps.core.utils.views import PageTitleMixin

from . import forms, models, tasks


class List(PermissionRequiredMixin, PageTitleMixin, generic.ListView):
    """List of recent batches, with links to utilities
    Todo: convert to a datatable for easy pagination
    """

    permission_required = 'hesa_data_futures.view_batch'
    queryset = models.Batch.objects.order_by('-pk')[:10]
    title = 'HESA Data Futures'
    subtitle = 'Batch list'
    template_name = 'hesa_data_futures/list.html'


class View(PermissionRequiredMixin, PageTitleMixin, tables.views.SingleTableMixin, generic.DetailView):
    """Generic datatable to view all the records in any of the hesa tables"""

    permission_required = 'hesa.view_batch'
    model = models.Batch
    template_name = 'hesa_data_futures/view.html'
    title = 'HESA Data Futures'

    model_map: dict[str, Model] = {
        'course': models.Course,
        'qualification': models.Qualification,
        'student': models.Student,
        'module': models.Module,
        'session_year': models.SessionYear,
        'venue': models.Venue,
    }

    def get_table(self, **kwargs) -> tables.Table:
        """Produce a generic table for a given model, excluding a couple common fields"""
        model = self.model_map.get(self.kwargs.get('model_name'), models.Course)
        table_class = tables.table_factory(model=model, fields=model.xml_fields)
        return table_class(data=model.objects.filter(batch=self.object), request=self.request)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['models'] = {key: model._meta.verbose_name.title() for key, model in self.model_map.items()}
        return context


class Create(PermissionRequiredMixin, PageTitleMixin, generic.FormView):
    permission_required = 'hesa_data_futures.add_batch'
    form_class = forms.CreateBatchForm
    title = 'HESA Data Futures'
    subtitle = 'Create batch'
    template_name = 'core/form.html'

    def form_valid(self, form) -> http.HttpResponse:
        task = tasks.create_return.delay(
            academic_year=form.cleaned_data['year'], created_by=self.request.user.username
        )
        return redirect('task:progress', task_id=task.id)


class BuildXML(PermissionRequiredMixin, generic.View):
    """Rebuilds an existing batch's XML file"""

    permission_required = 'hesa_data_futures.add_batch'

    def post(self, request, *args, **kwargs) -> http.HttpResponse:
        batch = get_object_or_404(models.Batch, pk=self.kwargs['pk'])
        task = tasks.create_hesa_xml.delay(batch_id=batch.id)
        return redirect('task:progress', task_id=task.id)


class Delete(PermissionRequiredMixin, PageTitleMixin, generic.DeleteView):
    permission_required = 'hesa_data_futures.delete_batch'
    model = models.Batch
    template_name = 'core/delete_form.html'

    def get_success_url(self) -> str:
        messages.success(self.request, f'Batch #{self.object.id} deleted')
        return reverse('hesa_data_futures:list')


class DownloadXML(PermissionRequiredMixin, generic.View):
    permission_required = 'hesa_data_futures.view_batch'

    def get(self, request, *args, **kwargs) -> http.HttpResponse:
        batch = get_object_or_404(models.Batch, pk=self.kwargs['pk'])
        path = settings.PROTECTED_MEDIA_URL + 'hesa_data_futures/' + batch.filename
        return http.HttpResponse(
            content_type='',
            headers={'X-Accel-Redirect': path, 'Content-Disposition': f'attachment;filename={batch.filename}'},
        )
