import factory

from apps.tutor.tests.factories import TutorModuleFactory

from .. import models


class TutorFeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TutorFee

    tutor_module = factory.SubFactory(TutorModuleFactory)
    type_id = 2  # todo: an enum
    amount = 100
