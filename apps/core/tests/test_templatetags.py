from datetime import datetime
from types import SimpleNamespace

from django.template import Context, Template
from django.test import TestCase


class TestTemplateTags(TestCase):
    @staticmethod
    def render_template(string, context=None):
        context = Context(context or {})
        return Template(string).render(context)

    def test_timestamp(self):
        obj = SimpleNamespace(
            created_by='testuser',
            created_on=datetime(2020, 1, 1, 12),
        )

        rendered = self.render_template(
            """
                {% load redpot_tags %}
                {% timestamp object %}
            """,
            {'object': obj},
        )
        self.assertInHTML('1 Jan 2020 12:00', rendered)
