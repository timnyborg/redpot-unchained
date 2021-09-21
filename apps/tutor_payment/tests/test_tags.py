from django import template, test

from ..models import TutorPayment


class TestStatusIcon(test.TestCase):
    def test_render(self):
        context = template.Context({'obj': TutorPayment()})
        template_to_render = template.Template('{% load tutor_payment_tags %}{% payment_status_icon obj %}')
        rendered_template = template_to_render.render(context)
        self.assertIn('Raised', rendered_template)
        self.assertTemplateUsed('tags/payment_status_tag.html')
