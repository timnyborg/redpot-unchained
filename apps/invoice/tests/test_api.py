import factory
from rest_framework import status, test

from django.urls import reverse

from apps.core.utils.tests import LoggedInMixin

from .. import models
from . import factories


class TestSaveSchedule(LoggedInMixin, test.APITestCase):
    superuser = True

    def test_save_replaces_schedule(self):
        """Check that existing schedule items are removed when posting a new schedule"""
        plan = factories.CustomPaymentPlanFactory()
        url = reverse('invoice:save-payment-schedule', kwargs={'plan_id': plan.id})
        old_payment = factories.ScheduledPaymentFactory(payment_plan=plan)

        # A simple way of producing dicts from a factory_boy class.  See:
        # https://factoryboy.readthedocs.io/en/stable/recipes.html#converting-a-factory-s-output-to-a-dict
        data = factory.build_batch(dict, FACTORY_CLASS=factories.ScheduledPaymentFactory, size=2)
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(plan.scheduled_payments.count(), 2)
        with self.assertRaises(models.ScheduledPayment.DoesNotExist):
            old_payment.refresh_from_db()
