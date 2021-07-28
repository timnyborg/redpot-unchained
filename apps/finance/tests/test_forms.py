from django import test

from apps.enrolment.tests.factories import EnrolmentFactory

from .. import forms


class TestMultipleEnrolmentPaymentForm(test.TestCase):
    def test_amount_validation(self):
        enrolment = EnrolmentFactory()
        form = forms.MultipleEnrolmentPaymentForm(
            enrolments=[enrolment],
            data={
                f'allocation_{enrolment.pk}': 10,
                'amount': 20,
            },
        )
        # Check for an error message listing the true sum
        self.assertTrue(any('10' in message for message in form.errors['amount']))
