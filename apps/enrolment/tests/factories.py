import factory

from apps.module.tests.factories import ModuleFactory
from apps.programme.tests.factories import QAFactory

from .. import models


class EnrolmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Enrolment

    module = factory.SubFactory(ModuleFactory)
    qa = factory.SubFactory(QAFactory)
    status_id = 10  # todo: enum
