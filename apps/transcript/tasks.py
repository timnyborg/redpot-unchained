from datetime import date, datetime
from io import BytesIO

from celery_progress.backend import ProgressRecorder
from PyPDF2 import PdfFileMerger

from django.conf import settings

from apps.enrolment.models import Enrolment
from apps.student.models import Student
from redpot.celery import app

from . import pdfs


@app.task(name='create_transcript_batch', bind=True)
def create_batch(self, *, level: str, header: bool, created_by: str):
    """Bulk PDF production of all unprinted UG transcripts"""
    recorder = ProgressRecorder(self)

    if level == 'undergraduate':
        level_filter = {'qa__programme__qualification_id': 61}  # todo: flags
        historical_cutoff = date(2010, 1, 1)
    elif level == 'postgraduate':
        # Only health sciences at the moment.
        # todo: use a programme flag, or make universal if student admin wants.
        #       then level_filter can move to transcript_printable() with an arg
        level_filter = {'qa__programme_id': 170}
        historical_cutoff = date(2016, 1, 1)
    else:
        raise ValueError(f'Invalid level: {level}')

    students = list(
        Enrolment.objects.transcript_printable()
        .filter(
            **level_filter,
            created_on__gt=historical_cutoff,
            transcript_date__isnull=True,
        )
        .order_by('qa__student')
        .values_list('qa__student', flat=True)
        .distinct()
    )

    merger = PdfFileMerger()

    for index, student_id in enumerate(students):
        student = Student.objects.get(pk=student_id)  # todo: get the student objects directly from the queryset
        transcript = pdfs.create_transcript(header=header, level=level, student=student, mark_printed=True)
        merger.append(BytesIO(transcript))
        recorder.set_progress(current=index, total=len(students), description='Todo')

    # create the media subfolder if required
    file_path = settings.PROTECTED_MEDIA_ROOT / 'transcripts'
    file_path.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    title = f'{level}_transcripts_{now:%Y-%m-%d_%H%M%S}_{created_by}.pdf'
    filename = file_path / title

    with open(filename, 'wb') as output:
        merger.write(output)

    return {'progress': 'could go here'}  # TODO: figure out what to return
