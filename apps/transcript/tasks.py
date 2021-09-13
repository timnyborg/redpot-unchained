from celery_progress.backend import ProgressRecorder

from redpot.celery import app


@app.task(name='create_transcript_batch', bind=True)
def create_batch(self, *, level: str, header: bool, created_by: str):
    recorder = ProgressRecorder(self)

    ...

    return {'progress': 'could go here'}  # TODO: figure out what to return
