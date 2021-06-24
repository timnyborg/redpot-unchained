from celery_progress.backend import ProgressRecorder

from redpot.celery import app

from . import services


@app.task(name='create_hesa_return', bind=True)
def create_return(self, *, academic_year: int, created_by: str):
    recorder = ProgressRecorder(self)

    services.create_return(academic_year, created_by, recorder=recorder)
    return {'progress': 'could go here'}  # TODO: figure out what to return
