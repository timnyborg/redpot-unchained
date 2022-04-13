import string

from django import test
from django.core.exceptions import ImproperlyConfigured

from . import factories


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
