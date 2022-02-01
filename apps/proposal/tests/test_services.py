from datetime import date

from django import test

from apps.module.tests.factories import ModuleFactory
from apps.tutor.tests.factories import TutorFactory

from .. import models, services


class TestPopulateFromModel(test.TestCase):
    def test_populate_from_module(self):
        module = ModuleFactory(start_date=date(2000, 1, 1), teaching_outcomes='text')
        tutor = TutorFactory()
        proposal = models.Proposal(module=module, tutor=tutor)

        services.populate_from_module(proposal=proposal)

        proposal.refresh_from_db()
        self.assertEqual(proposal.title, module.title)
        self.assertEqual(proposal.teaching_outcomes, module.teaching_outcomes)
        self.assertEqual(proposal.start_date, module.start_date)
