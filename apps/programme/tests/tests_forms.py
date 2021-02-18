from django.test import TestCase
from ..forms import ProgrammeEditForm


class TestEditForm(TestCase):
    def test_form(self):
        class FakeUser:
            def has_perm(self, *args, **kwargs):
                return True

        form = ProgrammeEditForm(
            data={
                "title": "Title",
                "division": 1,
                "portfolio": 1,
                "qualification": 1,
            },
            user=FakeUser()
        )
        self.assertFalse(
            form.errors
        )
