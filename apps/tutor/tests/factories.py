import factory

from apps.module.tests.factories import ModuleFactory
from apps.student.tests.factories import StudentFactory

from .. import models


class TutorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Tutor

    student = factory.SubFactory(StudentFactory)
    appointment_id = factory.Faker('numerify', text='CASTCH%#####')
    employee_no = factory.Faker('numerify', text='%######')


class TutorModuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TutorModule

    tutor = factory.SubFactory(TutorFactory)
    module = factory.SubFactory(ModuleFactory)
