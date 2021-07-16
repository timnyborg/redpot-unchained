from django import test

from apps.core.utils.tests import LoggedInViewTestMixin
from apps.fee.tests.factories import FeeFactory
from apps.finance.services import add_enrolment_fee

from . import factories


class TestViewPage(LoggedInViewTestMixin, test.TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Setup an enrolment with one fee added
        cls.enrolment = factories.EnrolmentFactory()
        cls.fee = FeeFactory(module=cls.enrolment.module)
        add_enrolment_fee(
            enrolment_id=cls.enrolment.id,
            fee_id=cls.fee.id,
            user=cls.user,
        )
        cls.url = cls.enrolment.get_absolute_url()

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.fee.description)
