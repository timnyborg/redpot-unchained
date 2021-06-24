from datetime import date
from unittest import mock

import freezegun

from django import test
from django.core import mail

from .. import tasks
from . import factories


class TestMassModuleStatusUpdate(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.module = factories.ModuleFactory(
            publish_date=date(2020, 1, 1),
            start_date=date(2020, 2, 1),
            end_date=date(2020, 3, 1),
            unpublish_date=date(2021, 1, 1),
            auto_publish=True,
            is_published=False,
            email='test@conted.ox.ac.uk',
        )

    @freezegun.freeze_time(date(2020, 2, 1))
    @mock.patch('apps.module.models.Module.is_publishable', True)  # Avoids building a complete, publishable module
    def test_auto_publish(self):
        modules_checked = tasks.update_module_statuses()
        self.assertEqual(modules_checked, 1)
        self.module.refresh_from_db()
        self.assertTrue(self.module.is_published)
        # Check the email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.module.title, mail.outbox[0].body)
