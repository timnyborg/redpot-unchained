import string

from django import test
from django.core.exceptions import ImproperlyConfigured

from . import factories


class TestAddressFlags(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = factories.StudentFactory()
        cls.initial_default = factories.AddressFactory(student=cls.student, is_default=True, is_billing=True)

    def test_creating_new_billing_unsets_old(self):
        """Check that creating a new billing address un-sets the old"""
        factories.AddressFactory(student=self.student, is_billing=True)
        self.initial_default.refresh_from_db()
        self.assertFalse(self.initial_default.is_billing)

    def test_updating_new_billing_unsets_old(self):
        """Check that updating an address to billing un-sets the old"""
        new_billing = factories.AddressFactory(student=self.student, is_billing=False)
        new_billing.is_billing = True
        new_billing.save()
        self.initial_default.refresh_from_db()
        self.assertFalse(self.initial_default.is_billing)

    def test_creating_new_default_unsets_old(self):
        """Check that creating a new billing address un-sets the old"""
        factories.AddressFactory(student=self.student, is_default=True)
        self.initial_default.refresh_from_db()
        self.assertFalse(self.initial_default.is_default)

    def test_updating_new_default_unsets_old(self):
        """Check that updating an address to billing un-sets the old"""
        new_default = factories.AddressFactory(student=self.student, is_billing=False)
        new_default.is_default = True
        new_default.save()
        self.initial_default.refresh_from_db()
        self.assertFalse(self.initial_default.is_default)

    def test_deleting_default_sets_other(self):
        """Check that deleting the default address sets the next in line"""
        new_default = factories.AddressFactory(student=self.student, is_default=False)
        self.initial_default.delete()
        new_default.refresh_from_db()
        self.assertTrue(new_default.is_default)


class TestStudentModel(test.TestCase):
    def test_deceased_wipes_marketing_fields(self):
        student = factories.StudentFactory.build(no_publicity=False, mail_optin=True, email_optin=True)
        student.deceased = True
        student.save()
        self.assertTrue(student.no_publicity and not student.mail_optin and not student.email_optin)


class TestMoodleID(test.SimpleTestCase):
    @test.override_settings(MOODLE_PASSWORD_COMPONENTS=list(string.ascii_letters))
    def test_password_generation_idempotent(self):
        moodle_id = factories.MoodleFactory.build(first_module_code='O20XXX000')
        first = moodle_id.initial_password
        second = moodle_id.initial_password
        self.assertEqual(first, second)

    @test.override_settings(MOODLE_PASSWORD_COMPONENTS=[])
    def test_password_generation_requires_components(self):
        moodle_id = factories.MoodleFactory.build(first_module_code='O20XXX000')
        with self.assertRaises(ImproperlyConfigured):
            moodle_id.initial_password
