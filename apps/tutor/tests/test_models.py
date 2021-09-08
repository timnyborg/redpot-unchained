from datetime import date

from freezegun import freeze_time

from django.test import SimpleTestCase

from .factories import TutorFactory


@freeze_time('2020-01-01')
class TestRTWExpired(SimpleTestCase):
    def test_expired(self):
        tutor = TutorFactory.build(rtw_end_date=date(1999, 1, 1))
        self.assertTrue(tutor.rtw_expired())

    def test_not_expired(self):
        tutor = TutorFactory.build(rtw_end_date=date(2025, 1, 1))
        self.assertFalse(tutor.rtw_expired())


@freeze_time('2020-01-01')
class TestRTWExpiresSoon(SimpleTestCase):
    def test_expiring_soon(self):
        tutor = TutorFactory.build(rtw_end_date=date(1999, 6, 1))
        self.assertTrue(tutor.rtw_expires_soon())

    def test_not_expiring_soon(self):
        tutor = TutorFactory.build(rtw_end_date=date(2025, 1, 1))
        self.assertFalse(tutor.rtw_expires_soon())
