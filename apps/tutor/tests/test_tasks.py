from datetime import datetime

from freezegun import freeze_time

from django import test

from .. import tasks
from . import factories


@freeze_time(datetime(2020, 1, 1))
class TestRemoveOldBankingDetails(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tutor = factories.TutorFactory(
            nino='ABCDEFGH12A',
            accountname='Fred',
            swift='ABCDEF12',
            created_on=datetime(2010, 1, 1),
            modified_on=datetime(2010, 1, 1),
        )

    def test_no_module_history_includes_tutor(self):
        removed = tasks.remove_old_banking_details(years=6, months=0)
        self.assertEqual(removed, 1)

        # also check it does what it says on the tin
        self.tutor.refresh_from_db()
        self.assertEqual(self.tutor.nino, '')
        self.assertEqual(self.tutor.accountname, '')
        self.assertEqual(self.tutor.swift, '')

    @freeze_time(datetime(2010, 2, 1))
    def test_recent_modification_excludes_tutor(self):
        removed = tasks.remove_old_banking_details()
        self.assertEqual(removed, 0)

        self.tutor.refresh_from_db()
        self.assertNotEqual(self.tutor.nino, '')

    def test_recent_module_excludes_tutor(self):
        factories.TutorModuleFactory(tutor=self.tutor, module__start_date=datetime(2018, 1, 1))
        factories.TutorModuleFactory(tutor=self.tutor, module__start_date=datetime(2013, 1, 1))
        removed = tasks.remove_old_banking_details(years=6, months=0)
        self.assertEqual(removed, 0)

    def test_recent_module_creation_excludes_tutor(self):
        factories.TutorModuleFactory(
            tutor=self.tutor, module__start_date=None, module__created_on=datetime(2018, 1, 1)
        )
        factories.TutorModuleFactory(tutor=self.tutor, module__start_date=datetime(2013, 1, 1))
        removed = tasks.remove_old_banking_details(years=6, months=0)
        self.assertEqual(removed, 0)

    def test_old_module_includes_tutor(self):
        factories.TutorModuleFactory(tutor=self.tutor, module__start_date=datetime(2013, 1, 1))
        removed = tasks.remove_old_banking_details(years=6, months=0)
        self.assertEqual(removed, 1)
