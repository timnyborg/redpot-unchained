import factory

from apps.module.tests.factories import ModuleFactory
from apps.qualification_aim.tests.factories import QualificationAimFactory

from .. import models


class EnrolmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Enrolment

    module = factory.SubFactory(ModuleFactory)
    qa = factory.SubFactory(QualificationAimFactory)
    status_id = 10  # todo: enum
