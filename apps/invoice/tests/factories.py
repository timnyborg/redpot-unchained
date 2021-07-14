import factory

from .. import models


class InvoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Invoice

    number = factory.Sequence(lambda n: n)
    amount = 100
