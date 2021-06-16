import factory

from apps.programme.tests.factories import ProgrammeFactory
from apps.student.tests.factories import StudentFactory

from .. import models


class QualificationAimFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.QualificationAim

    student = factory.SubFactory(StudentFactory)
    programme = factory.SubFactory(ProgrammeFactory)
    entry_qualification_id = 'C90'
