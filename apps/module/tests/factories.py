import string

import factory

from .. import models


class ModuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Module

    code = factory.Faker('bothify', text='F99F###???', letters=string.ascii_uppercase)
    title = factory.sequence(lambda n: f'Module #{n}')

    cost_centre = factory.Faker('bothify', text='X?####', letters='ABCDEFG')
    activity_code = factory.Faker('numerify', text='##')
    source_of_funds = factory.Faker('bothify', text='X?###', letters='ABCDEFG')


class FeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Fee

    description = factory.Sequence(lambda n: f'Fee #{n}')
    amount = factory.Faker('pyfloat', min_value=1, max_value=10000, right_digits=2)
    module = factory.SubFactory(ModuleFactory)
