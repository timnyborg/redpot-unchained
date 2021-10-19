from django.test import SimpleTestCase

from apps.module.models import Module

from ..utils.expense_forms import template_options


class TestExpenseTemplateOptions(SimpleTestCase):
    """Check that the correct options are present / absent"""

    def test_accredited_module(self):
        module = Module(non_credit_bearing=False)
        options = template_options(module)
        self.assertIn('day_weekend', options)
        self.assertNotIn('nonaccredited', options)

    def test_nonaccredited_module(self):
        module = Module(non_credit_bearing=True)
        options = template_options(module)
        self.assertIn('nonaccredited', options)
        self.assertNotIn('day_weekend', options)
