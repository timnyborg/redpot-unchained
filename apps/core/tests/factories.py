import factory

from .. import models


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.User

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.LazyAttribute(lambda o: f'{o.first_name}.{o.last_name}@conted.ox.ac.uk'.lower())
    username = factory.LazyAttribute(lambda o: f'{o.last_name[:7]}{o.first_name[0]}')
