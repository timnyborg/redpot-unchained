from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import generic

# todo: permissions
from apps.core.utils.views import PageTitleMixin

from . import forms, models, tasks


class ListBatches(LoginRequiredMixin, PageTitleMixin, generic.ListView):
    queryset = models.Batch.objects.order_by('-pk')[:10]
    title = 'HESA'
    subtitle = 'Batch list'
    template_name = 'hesa/list_batches.html'


class CreateBatch(LoginRequiredMixin, PageTitleMixin, generic.FormView):
    form_class = forms.CreateBatchForm
    title = 'HESA'
    subtitle = 'Create batch'
    template_name = 'core/form.html'

    def form_valid(self, form):
        task = tasks.create_return.delay(
            academic_year=form.cleaned_data['year'], created_by=self.request.user.username
        )
        return redirect('task:progress', task_id=task.id)
