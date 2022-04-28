from celery_progress.backend import ProgressRecorder

from redpot.celery import app

from . import models, services


@app.task(name='create_data_futures_return', bind=True)
def create_return(self, *, academic_year: int, created_by: str):
    recorder = ProgressRecorder(self)
    batch = services.create_return(academic_year, created_by, recorder=recorder)
    recorder.set_progress(current=2, total=2, description='Generating XML')
    services.save_xml(batch=batch)
    return {'redirect': batch.get_absolute_url()}


@app.task(name='create_data_futures_xml', bind=True)
def create_hesa_xml(self, *, batch_id: int):
    recorder = ProgressRecorder(self)
    batch = models.Batch.objects.get(pk=batch_id)
    recorder.set_progress(current=1, total=1, description='Generating XML')
    services.save_xml(batch=batch)
    return {'redirect': batch.get_absolute_url()}
