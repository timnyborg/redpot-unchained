import factory

from .. import models


class InvoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Invoice

    number = factory.Sequence(lambda n: n)


class LedgerFactory(factory.django.DjangoModelFactory):
    # Requires an enrolment object (at the moment)
    class Meta:
        model = models.Ledger

    amount = factory.Faker('pyint')
    date = factory.Faker('date')
    type_id = 1  # todo: enum
    allocation = 1
