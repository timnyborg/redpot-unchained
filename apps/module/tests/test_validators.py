from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from ..models import Module


class TestModuleValidators(TestCase):
    def setUp(self):
        self.module = Module(
            title='Test module',
            code='T12T123TTT',
        )

    def test_finance_code_success(self):
        try:
            self.module.cost_centre = 'XB1000'
            self.module.activity_code = '15'
            self.module.source_of_funds = 'XA123'
            self.module.full_clean()
        except ValidationError as e:
            self.fail(e)

    def test_finance_code_exception(self):
        self.module.activity_code = '4'
        self.assertRaises(ValidationError, self.module.full_clean)

        self.module.source_of_funds = 'XA123B'
        self.assertRaises(ValidationError, self.module.full_clean)

    def test_url_created_when_empty(self):
        self.module.url = None
        self.module.save()
        self.assertIsNotNone(self.module.url)

    def test_start_and_end_date_success(self):
        # End date without start date
        self.module.end_date = date(2000, 1, 1)
        self.assertRaises(ValidationError, self.module.full_clean)

        # End date before start date
        self.module.start_date = date(2001, 1, 1)
        self.assertRaises(ValidationError, self.module.full_clean)

    def test_start_and_end_date_exception(self):
        self.module.start_date = date(2001, 1, 1)
        self.module.end_date = date(2002, 1, 1)
        try:
            self.module.full_clean()
        except ValidationError as e:
            self.fail(e)

    def test_hilary_and_michaelmas_exception(self):
        # Michaelmas without Hilary
        self.module.michaelmas_end = date(2001, 1, 1)
        self.assertRaises(ValidationError, self.module.full_clean)

    def test_hilary_and_michaelmas_success(self):
        # Valid dates
        self.module.michaelmas_end = date(2001, 1, 1)
        self.module.hilary_start = date(2002, 1, 1)
        try:
            self.module.full_clean()
        except ValidationError as e:
            self.fail(e)
