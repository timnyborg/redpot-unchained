from unittest import mock

from django import test
from django.urls import reverse

from apps.application.tests import factories
from apps.core.utils.tests import LoggedInMixin, LoggedInViewTestMixin
from apps.enrolment.tests.factories import EnrolmentFactory


@mock.patch('apps.application.services.enrol_applicant')
class TestCreateAndEnrolStudentView(LoggedInMixin, test.TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.application = factories.ApplicationFactory()
        cls.url = reverse('application:enrol-student', kwargs={'pk': cls.application.pk})

    def test_enrol_service_called(self, patched_service: mock.MagicMock):
        self.client.post(path=self.url)
        patched_service.assert_called_once()

    def test_fails_if_already_enrolled(self, patched_service: mock.MagicMock):
        EnrolmentFactory(module=self.application.module, qa__student=self.application.student)
        self.client.post(path=self.url)
        patched_service.assert_not_called()


class TestDetailView(LoggedInViewTestMixin, test.TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.application = factories.ApplicationFactory()
        cls.url = reverse('application:view', kwargs={'pk': cls.application.pk})
