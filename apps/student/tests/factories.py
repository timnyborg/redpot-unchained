import factory

from .. import models


class StudentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Student

    firstname = factory.Faker('first_name')
    surname = factory.Faker('last_name')
