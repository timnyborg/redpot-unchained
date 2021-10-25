import factory

from apps.core.tests.factories import UserFactory
from apps.tutor.tests.factories import TutorModuleFactory

from .. import models


class PaymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TutorPayment

    tutor_module = factory.SubFactory(TutorModuleFactory)
    approver = factory.SubFactory(UserFactory)
    type_id = 2  # todo: an enum
    amount = 100
    weeks = 1
