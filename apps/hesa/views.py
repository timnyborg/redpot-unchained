from django import http
from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

# todo: permissions
from apps.core.utils.views import PageTitleMixin

from . import forms, models, tasks


class ListBatches(PermissionRequiredMixin, PageTitleMixin, generic.ListView):
    permission_required = 'hesa.view_batch'
    queryset = models.Batch.objects.order_by('-pk')[:10]
    title = 'HESA'
    subtitle = 'Batch list'
    template_name = 'hesa/list_batches.html'


class CreateBatch(PermissionRequiredMixin, PageTitleMixin, generic.FormView):
    permission_required = 'hesa.add_batch'
    form_class = forms.CreateBatchForm
    title = 'HESA'
    subtitle = 'Create batch'
    template_name = 'core/form.html'

    def form_valid(self, form):
        task = tasks.create_return.delay(
            academic_year=form.cleaned_data['year'], created_by=self.request.user.username
        )
        return redirect('task:progress', task_id=task.id)


class DownloadXML(PermissionRequiredMixin, generic.View):
    permission_required = 'hesa.view_batch'

    def get(self, request, *args, **kwargs) -> http.HttpResponse:
        batch = get_object_or_404(models.Batch, pk=self.kwargs['pk'])
        path = settings.PROTECTED_MEDIA_URL + 'hesa/' + batch.filename
        return http.HttpResponse(
            content_type='',
            headers={'X-Accel-Redirect': path, 'Content-Disposition': f'attachment;filename={batch.filename}'},
        )
