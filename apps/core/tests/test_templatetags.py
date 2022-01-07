import dataclasses
from datetime import datetime
from typing import Optional

from django import test
from django.template import Context, Template


def render_template(template_string: str, context: Optional[dict] = None) -> str:
    context = Context(context or {})
    return Template(template_string).render(context)


class TestTimestamp(test.TestCase):
    @dataclasses.dataclass
    class Timestamped:
        created_by: str
        created_on: datetime

    def test_timestamp(self):
        obj = self.Timestamped(created_by='testuser', created_on=datetime(2020, 1, 1, 12))
        rendered = render_template(
            """
                {% load redpot_tags %}
                {% timestamp object %}
            """,
            context={'object': obj},
        )
        self.assertInHTML('1 Jan 2020 12:00', rendered)


@test.override_settings(SQUARE_URL='https://square')
class TestSquareURL(test.SimpleTestCase):
    def test_square_url(self):
        rendered = render_template(
            """
                {% load redpot_tags %}
                {% square_url 'Dir' 'Subdir' 'Report' code=1 val=2 %}
            """,
        )
        self.assertIn('https://square/report/Dir/Subdir/Report?code=1&val=2', rendered)
