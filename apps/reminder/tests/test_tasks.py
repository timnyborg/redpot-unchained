from datetime import date
from unittest import mock

from freezegun import freeze_time

from django import test

from apps.module.tests.factories import ModuleFactory

from .. import tasks


@freeze_time(date(2020, 1, 1))
@mock.patch('apps.reminder.services.mail_module_reminders')
class TestReminderMailing(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.module = ModuleFactory(start_date=date(2020, 1, 11), email='test@conted.ox.ac.uk', auto_reminder=True)

    def test_correct_date_offset(self, mocked_service: mock.MagicMock):
        result = tasks.mail_reminders(days=10)
        self.assertEqual(result, 1)
        mocked_service.assert_called_once_with(module=self.module)

    def test_incorrect_date_offset(self, mocked_service: mock.MagicMock):
        result = tasks.mail_reminders(days=15)
        self.assertEqual(result, 0)
        mocked_service.assert_not_called()

    def test_ignores_cancelled(self, mocked_service: mock.MagicMock):
        self.module.is_cancelled = True
        self.module.save()
        result = tasks.mail_reminders(days=10)
        self.assertEqual(result, 0)
        mocked_service.assert_not_called()

    def test_ignores_already_sent(self, mocked_service: mock.MagicMock):
        self.module.reminder_sent_on = date(2019, 12, 1)
        self.module.save()
        result = tasks.mail_reminders(days=10)
        self.assertEqual(result, 0)
        mocked_service.assert_not_called()

    def test_requires_auto_reminder(self, mocked_service: mock.MagicMock):
        self.module.auto_reminder = False
        self.module.save()
        result = tasks.mail_reminders(days=10)
        self.assertEqual(result, 0)
        mocked_service.assert_not_called()

    def test_requires_email(self, mocked_service: mock.MagicMock):
        self.module.email = ''
        self.module.save()
        result = tasks.mail_reminders(days=10)
        self.assertEqual(result, 0)
        mocked_service.assert_not_called()
