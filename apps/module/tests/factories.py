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


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Book

    module = factory.SubFactory(ModuleFactory)
    title = factory.Faker('sentence', nb_words=4)
    author = factory.Faker('name')
