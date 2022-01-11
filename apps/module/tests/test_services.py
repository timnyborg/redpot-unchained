from datetime import datetime
from unittest.mock import MagicMock

from django.test import SimpleTestCase, TestCase

from apps.fee.tests.factories import FeeFactory
from .factories import ModuleFactory

from .. import models, services
from apps.enrolment.tests.factories import EnrolmentFactory
from ...student.tests.factories import EmailFactory


class TestClone(SimpleTestCase):
    def setUp(self):
        self.source = models.Module(
            title='Source title', start_date=datetime, url='source-title', division_id=1, snippet='A test module'
        )
        self.target = models.Module(
            title='Target title',
        )

    def test_default_fields_copied(self):
        services.clone_fields(source=self.source, target=self.target)
        self.assertEqual(self.source.snippet, self.target.snippet)
        self.assertEqual(self.source.division_id, self.target.division_id)
        self.assertIsNone(self.target.url)
        self.assertIsNone(self.target.start_date)

    def test_copy_url(self):
        services.clone_fields(source=self.source, target=self.target, copy_url=True)
        self.assertEqual(self.source.url, self.target.url)

    def test_copy_dates(self):
        services.clone_fields(source=self.source, target=self.target, copy_dates=True)
        self.assertEqual(self.source.start_date, self.target.start_date)


class TestCopyFees(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.source = models.Module.objects.create(
            title='Source title',
            code='T00T000TTT',
        )
        cls.target = models.Module.objects.create(
            title='Target title',
            code='T01T000TTT',
        )
        FeeFactory(
            module=cls.source,
            amount=100,
        )

    def test_copy(self):
        user = MagicMock()
        user.username = 'testuser'
        services.copy_fees(source=self.source, target=self.target, user=user)
        fees = self.target.fees.all()
        self.assertEqual(len(fees), 1)
        self.assertEqual(fees.first().amount, 100)

class TestEmailingModuleStudents(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.module = ModuleFactory()
        cls.enrolments = EnrolmentFactory.create_batch(
            size=2,
            module=cls.module
        )
        EmailFactory(student=cls.enrolments[0].qa.student)

    def test_email_module_students(self):
        result = services.email_module_students(module=self.module, email_subject='test', email_message='test message')
        self.assertEqual(result, 1)
