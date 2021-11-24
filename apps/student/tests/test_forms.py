from dataclasses import dataclass
from datetime import date

from freezegun import freeze_time
from parameterized import parameterized

from django import test
from django.core.exceptions import ValidationError

from .. import forms
from . import factories


@dataclass
class CountryStub:
    name: str


class TestAddressForm(test.SimpleTestCase):
    @parameterized.expand(
        [
            ('valid', 'United Kingdom - England', 'OX1 2JA', 'OX1 2JA'),
            ('empty', 'United Kingdom - England', '', ''),
            ('reformat', 'United Kingdom - England', 'ox342 j A  ', 'OX34 2JA'),
            ('non-uk', 'Canada', 'S7N 1R5', 'S7N 1R5'),
        ]
    )
    def test_postcode_processing(self, name: str, country: str, postcode: str, expected: str):
        form = forms.AddressForm()
        form.cleaned_data = {
            'country': CountryStub(country),
            'postcode': postcode,
        }
        self.assertEqual(form.clean_postcode(), expected)

    def test_invalid_uk_postcode(self):
        form = forms.AddressForm()
        form.cleaned_data = {
            'country': CountryStub('United Kingdom - England'),
            'postcode': 'OX1 2JAA',
        }
        with self.assertRaises(ValidationError):
            form.clean_postcode()

    def test_sits_field_locking(self):
        address = factories.AddressFactory.build(sits_type='H')
        form = forms.AddressForm(instance=address)
        self.assertTrue(form.fields['line1'].disabled)

    def test_no_sits_field_locking(self):
        address = factories.AddressFactory.build(sits_type=None)
        form = forms.AddressForm(instance=address)
        self.assertFalse(form.fields['line1'].disabled)


@freeze_time(date(2020, 1, 1))
class TestEditPersonForm(test.SimpleTestCase):
    def test_too_recent_birthdate(self):
        form = forms.EditForm()
        form.cleaned_data = {'birthdate': date(2015, 1, 1)}
        with self.assertRaises(ValidationError):
            form.clean_birthdate()

    def test_valid_birthdate(self):
        form = forms.EditForm()
        form.cleaned_data = {'birthdate': date(2000, 1, 1)}
        try:
            form.clean_birthdate()
        except ValidationError:
            self.fail('Valid birthdate failed validation')

    def test_null_birthdate(self):
        form = forms.EditForm()
        form.cleaned_data = {'birthdate': None}
        try:
            form.clean_birthdate()
        except ValidationError:
            self.fail('Valid birthdate failed validation')

    def test_display_restricted_fields(self):
        form = forms.EditForm(edit_restricted_fields=True)
        self.assertTrue('gender_identity' in form.fields)

    def test_hide_restricted_fields(self):
        form = forms.EditForm(edit_restricted_fields=False)
        self.assertFalse('gender_identity' in form.fields)
