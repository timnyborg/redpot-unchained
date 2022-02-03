import factory

from apps.module.tests.factories import ModuleFactory
from apps.student.tests.factories import StudentFactory

from .. import models


class ApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Application

    student = factory.SubFactory(StudentFactory)
    module = factory.SubFactory(ModuleFactory)

    firstname = factory.Faker('first_name')
    surname = factory.Faker('last_name')
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')
    address1 = factory.Faker('street_address')
    billing_address1 = factory.Faker('street_address')
    company_name = factory.Faker('company')
    academic_credit = True
