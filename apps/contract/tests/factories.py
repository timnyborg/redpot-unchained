import factory

from apps.core.tests.factories import UserFactory
from apps.tutor.tests.factories import TutorModuleFactory

from .. import models


class ContractFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Contract

    tutor_module = factory.SubFactory(TutorModuleFactory)
    status = models.Statuses.APPROVED_AWAITING_SIGNATURE
    type = models.Types.GUEST_SPEAKER
    options = {"full_name": "test"}
    approver = factory.SubFactory(UserFactory)
