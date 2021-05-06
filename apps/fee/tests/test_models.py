from django.core.exceptions import ValidationError
from django.test import TestCase

from ..models import FeeTypes, Limit
from . import factories


class TestFeeModel(TestCase):
    def test_catering_set_automatically(self):
        """Check that is_catering is set to True when using the catering type"""
        fee = factories.FeeFactory(type_id=FeeTypes.CATERING, is_catering=False)
        fee.full_clean()
        self.assertTrue(fee.is_catering)

    def test_limit_requires_accommodation(self):
        """Check that is_catering is set to True when using the catering type"""
        limit = Limit.objects.create(description='Test', places=10)
        fee = factories.FeeFactory(limit=limit)
        self.assertRaises(ValidationError, fee.full_clean)
        fee.is_single_accom = True
        try:
            fee.full_clean()
        except ValidationError:
            self.fail('fee.full_clean() raised ValidationError')
