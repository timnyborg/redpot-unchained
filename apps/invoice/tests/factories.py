import factory

from apps.enrolment.tests.factories import EnrolmentFactory

from .. import models


class InvoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Invoice

    number = factory.Sequence(lambda n: n)
    amount = 100


class LedgerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Ledger

    enrolment = factory.SubFactory(EnrolmentFactory)
    amount = factory.Faker('pyint')
    date = factory.Faker('date')
    type_id = 1  # todo: enum
    allocation = 1
