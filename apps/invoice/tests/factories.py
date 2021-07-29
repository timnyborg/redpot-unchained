import factory

from .. import models


class InvoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Invoice

    number = factory.Sequence(lambda n: n)
    amount = 100


class CustomPaymentPlanFactory(factory.django.DjangoModelFactory):
    """A payment plan with `custom` status and type, for testing bespoke schedules"""

    class Meta:
        model = models.PaymentPlan

    invoice = factory.SubFactory(InvoiceFactory)
    type_id = models.CUSTOM_PLAN_TYPE
    status_id = models.CUSTOM_PAYMENT_PENDING_STATUS
    amount = factory.Faker('pydecimal', min_value=1)


class ScheduledPaymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ScheduledPayment

    due_date = factory.Faker('date')
    amount = factory.Faker('pydecimal', min_value=1, left_digits=6, right_digits=2)
    is_deposit = False
