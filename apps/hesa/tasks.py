from celery_progress.backend import ProgressRecorder

from django.urls import reverse

from redpot.celery import app

from . import services


@app.task(name='create_hesa_return', bind=True)
def create_return(self, *, academic_year: int, created_by: str):
    recorder = ProgressRecorder(self)
    batch = services.create_return(academic_year, created_by, recorder=recorder)
    recorder.set_progress(current=12, total=12, description='Generating XML')
    services.save_xml(batch=batch)
    return {'redirect': reverse('hesa:xml', kwargs={'pk': batch.pk})}
