import factory

from apps.core.tests.factories import UserFactory
from apps.module.tests.factories import ModuleFactory
from apps.tutor.tests.factories import TutorFactory

from .. import models


class ProposalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Proposal

    tutor = factory.SubFactory(TutorFactory)
    module = factory.SubFactory(ModuleFactory)
    dos = factory.SubFactory(UserFactory)

    title = factory.SelfAttribute('module.title')  # Inherit from the source module
