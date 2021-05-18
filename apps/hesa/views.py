import json

from celery.result import AsyncResult

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import generic

from . import forms, models, tasks


class ListBatches(LoginRequiredMixin, generic.ListView):
    queryset = models.Batch.objects.order_by('-pk')[:10]
    template_name = 'hesa/list_batches.html'


class CreateBatch(LoginRequiredMixin, generic.FormView):
    form_class = forms.CreateBatchForm
    template_name = 'core/form.html'

    def form_valid(self, form):
        task = tasks.create_return.delay(
            academic_year=form.cleaned_data['year'], created_by=self.request.user.username
        )
        return redirect('hesa:status', task_id=task.id)


class TaskStatus(generic.View):
    def get(self, request, task_id):
        result = AsyncResult(task_id)
        response_data = {
            'state': result.state,
            'details': result.info,
        }
        if isinstance(response_data['details'], Exception):
            response_data['details'] = repr(response_data['details'])

        return JsonResponse(json.dumps(response_data), content_type='application/json', safe=False)

    #
    # options = [
    #     ('hesa_institution', 'Institution'),
    #     ('hesa_programme', 'Programme (course)'),
    #     ('hesa_programme_subject', 'Programme subject'),
    #     ('hesa_module', 'Module'),
    #     ('hesa_module-subject', 'Module subject'),
    #     ('hesa_student', 'Student'),
    #     ('hesa_qa', 'Qualification aim (instance)'),
    #     ('hesa_entry-profile', 'Entry profile'),
    #     ('hesa_award', 'Qualification awarded'),
    #     ('hesa_enrolment', 'Enrolment (student on module)'),
    # ]
    #
    # batches = idb().select(idb.hesa_batch.ALL, orderby=~idb.hesa_batch.id, limitby=(0, 10))
    #

    # if form.process().accepted:
    #     # Schedule the job, and redirect to the job-status page
    #     task = scheduler.queue_task(
    #         'create_return',
    #         [int(form.vars.year), auth.user.username, True],
    #         timeout=300,
    #         sync_output=2,
    #         group_name=LOCAL_SERVER if STAGING else 'main'
    #     )
    #     redirect(URL(status, args=task.id))
    #
    # return dict(form=form, options=options, batches=batches)
