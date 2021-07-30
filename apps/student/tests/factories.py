import factory

from .. import models


class StudentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Student

    firstname = factory.Faker('first_name')
    surname = factory.Faker('last_name')
    ethnicity = factory.Iterator(models.Ethnicity.objects.all())


class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Address

    student = factory.SubFactory(StudentFactory)
    line1 = factory.Faker('street_address')
    postcode = factory.Faker('postcode')
    town = factory.Faker('city')
    is_default = True


class StudentWithAddressFactory(StudentFactory):
    address = factory.RelatedFactory(AddressFactory, factory_related_name='student')
