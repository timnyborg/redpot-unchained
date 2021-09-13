from django import test
from django.urls import reverse

from apps.core.utils.tests import LoggedInViewTestMixin
from apps.enrolment.models import Results, Statuses
from apps.enrolment.tests.factories import EnrolmentFactory


class TestTranscript(LoggedInViewTestMixin, test.TestCase):
    superuser = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        enrolment = EnrolmentFactory(status_id=Statuses.CONFIRMED, result_id=Results.PASSED, points_awarded=10)
        student = enrolment.qa.student
        cls.url = reverse('transcript:undergraduate-headed', kwargs={'student_id': student.id})

    def test_get(self):
        """This can't actually verify the contents of the pdf"""
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/pdf')
