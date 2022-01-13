import factory

from apps.enrolment.tests.factories import EnrolmentFactory

from .. import models


class LedgerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Ledger

    enrolment = factory.SubFactory(EnrolmentFactory)
    amount = factory.Faker('pyint')
    timestamp = factory.Faker('date')
    type_id = models.TransactionTypes.FEE
    allocation = 1
    account_id = models.Accounts.DEBTOR  # todo: We may want a FeeFactory and PaymentFactory instead
