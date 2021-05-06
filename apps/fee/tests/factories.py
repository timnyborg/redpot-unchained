import factory

from apps.module.tests.factories import ModuleFactory

from .. import models


class FeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Fee

    description = factory.Sequence(lambda n: f'Fee #{n}')
    amount = factory.Faker('pydecimal', min_value=1, max_value=10000, right_digits=2)
    module = factory.SubFactory(ModuleFactory)
