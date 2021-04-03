from django import template, test

from ..models import TutorFee


class TestStatusIcon(test.TestCase):
    def test_render(self):
        context = template.Context({'obj': TutorFee()})
        template_to_render = template.Template('{% load tutor_payment_tags %}{% payment_status_icon obj %}')
        rendered_template = template_to_render.render(context)
        print('Raised', rendered_template)
        self.assertIn('Raised', rendered_template)
        self.assertTemplateUsed('tags/payment_status_tag.html')
