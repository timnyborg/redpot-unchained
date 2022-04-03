from celery_progress.backend import ProgressRecorder

from apps.module.models import Module
from redpot.celery import app

from . import client, services


@app.task(name='batch_cabs_module_bookings', bind=True)
def batch_cabs_module_bookings(self, *, module_ids: list):
    api_client = client.CABSApiClient()
    recorder = ProgressRecorder(self)
    modules = Module.objects.filter(id__in=module_ids)
    for index, module in enumerate(modules):
        recorder.set_progress(current=index, total=len(modules), description='Booking modules')
        services.create_module_bookings(module=module, api_client=api_client)
