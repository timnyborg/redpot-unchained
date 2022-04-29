from celery_progress.backend import ProgressRecorder

from redpot.celery import app

from . import models, services, xml


@app.task(name='create_data_futures_return', bind=True)
def create_return(self, *, academic_year: int, created_by: str):
    recorder = ProgressRecorder(self)
    batch = services.HESAReturn(academic_year, created_by, recorder=recorder).create()

    recorder.set_progress(current=2, total=3, description='Generating XML')
    tree = xml.generate_tree(batch)
    path = xml.save_xml(batch_id=batch.id, tree=tree)

    recorder.set_progress(current=2, total=3, description='Validating XML schema')
    errors = xml.validate_xml(tree)

    batch.filename = path
    batch.errors = errors
    batch.save()

    return {'redirect': batch.get_absolute_url()}


@app.task(name='create_data_futures_xml', bind=True)
def create_hesa_xml(self, *, batch_id: int):
    recorder = ProgressRecorder(self)
    batch = models.Batch.objects.get(pk=batch_id)

    recorder.set_progress(current=1, total=2, description='Generating XML')
    tree = xml.generate_tree(batch)
    path = xml.save_xml(batch_id=batch.id, tree=tree)

    recorder.set_progress(current=2, total=2, description='Validating XML schema')
    errors = xml.validate_xml(tree)

    batch.filename = path
    batch.errors = errors
    batch.save()

    return {'redirect': batch.get_absolute_url()}
