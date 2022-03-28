from datetime import date, datetime

from lxml import etree

from django import test
from django.urls import reverse

from apps.core.utils.tests import LoggedInMixin
from apps.fee.tests.factories import FeeFactory
from apps.module.models import ModuleFormat, Subject
from apps.module.tests.factories import ModuleFactory
from apps.tutor.tests.factories import TutorModuleFactory

from . import services


class TestXMLGenerators(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        ModuleFormat.objects.create(id=1, description='Format')
        cls.module = ModuleFactory(
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2020, 2, 1),
            portfolio_id=32,  # weekly
            code='O99P999XXX',
            format_id=1,
        )
        subject = Subject.objects.create(name='Subject', area='Area')
        cls.module.subjects.add(subject)
        cls.fee = FeeFactory(module=cls.module)
        cls.tutor = TutorModuleFactory(
            module=cls.module, is_teaching=True, is_published=True, tutor__qualifications='PhD'
        ).tutor

    def test_prospectus(self):
        # Get the first (only) xml tree produced, check that it contains the module
        xml_generator = services.prospectus(start_from=datetime(2019, 1, 1))
        _, xml = next(xml_generator)
        xml_string = etree.tostring(xml, encoding='utf-8').decode()

        self.assertIn(self.module.title, xml_string)
        self.assertIn(f'{self.fee.amount:.0f}', xml_string)

    def test_subject_brochures(self):
        # Get the first (only) xml tree produced, check that it contains the module
        xml_generator = services.subject_area_brochures(start_from=datetime(2019, 1, 1))
        _, xml = next(xml_generator)
        xml_string = etree.tostring(xml, encoding='utf-8').decode()

        self.assertIn(self.module.title, xml_string)
        self.assertIn('weekly-classes', xml_string)
        self.assertIn(self.tutor.student.firstname, xml_string)

    def test_newspaper(self):
        # Get the first (only) xml tree produced, check that it contains the module
        xml_generator = services.newspaper(start_from=datetime(2019, 1, 1))
        _, xml = next(xml_generator)
        xml_string = etree.tostring(xml, encoding='utf-8').decode()

        self.assertIn(self.module.title, xml_string)
        self.assertIn(f'{self.fee.amount:.0f}', xml_string)


class TestExportView(LoggedInMixin, test.TestCase):
    def test_produces_zip(self):
        response = self.client.post(
            reverse('marketing:export'),
            {'starting_from': date(2000, 1, 1), 'brochure_type': 'Prospectus'},
        )
        self.assertEqual(response.headers['content-type'], 'application/zip')
