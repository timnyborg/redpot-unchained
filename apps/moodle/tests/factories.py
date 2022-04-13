import factory

from apps.student.tests.factories import StudentFactory

from .. import models


class MoodleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.MoodleID

    student = factory.SubFactory(StudentFactory)
    moodle_id = factory.Sequence(lambda pk: 100000 + pk)
