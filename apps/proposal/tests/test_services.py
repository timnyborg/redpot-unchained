from datetime import date

from django import test
from django.core import mail

from apps.student.tests.factories import EmailFactory

from .. import services
from . import factories


class TestPopulateFromModule(test.TestCase):
    def test_populate_from_module(self):
        proposal = factories.ProposalFactory(module__start_date=date(2000, 1, 1), module__teaching_outcomes='text')

        services.populate_from_module(proposal=proposal)

        proposal.refresh_from_db()
        self.assertEqual(proposal.title, proposal.module.title)
        self.assertEqual(proposal.teaching_outcomes, proposal.module.teaching_outcomes)
        self.assertEqual(proposal.start_date, proposal.module.start_date)


class TestUpdateModule(test.TestCase):
    def test_update_module(self):
        proposal = factories.ProposalFactory(
            start_date=date(2000, 1, 1),
            teaching_outcomes='text',
            image='/test.png',
            title='New title',
        )

        services.update_module(proposal=proposal)

        proposal.module.refresh_from_db()
        self.assertEqual(proposal.title, proposal.module.title)
        self.assertEqual(proposal.teaching_outcomes, proposal.module.teaching_outcomes)
        self.assertEqual(proposal.start_date, proposal.module.start_date)
        self.assertEqual(proposal.image, proposal.module.image)


class TestAutoEmails(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.proposal = factories.ProposalFactory(module__email='admin@conted.ox.ac.uk')
        cls.tutor_email = EmailFactory(student=cls.proposal.tutor.student).email

    def test_tutor_prompt(self):
        services.email_tutor_prompt(proposal=self.proposal)
        self.assertIn(self.tutor_email, mail.outbox[0].to)
        self.assertIn(self.proposal.dos.first_name, mail.outbox[0].body)
        self.assertIn(self.proposal.module.title, mail.outbox[0].body)
        self.assertIn(self.proposal.tutor.student.firstname, mail.outbox[0].body)

    def test_dos_prompt(self):
        services.email_dos_prompt(proposal=self.proposal)
        self.assertIn(self.proposal.dos.email, mail.outbox[0].to)
        self.assertIn(self.proposal.dos.first_name, mail.outbox[0].body)

    def test_tutor_submission_confirmation(self):
        services.email_tutor_submission_confirmation(proposal=self.proposal)
        self.assertIn(self.tutor_email, mail.outbox[0].to)
        self.assertIn(self.proposal.tutor.student.firstname, mail.outbox[0].body)

    def test_admin_prompt(self):
        services.email_admin_prompt(proposal=self.proposal)
        self.assertIn(self.proposal.module.email, mail.outbox[0].to)
        self.assertIn(self.proposal.get_edit_url(), mail.outbox[0].alternatives[0][0])

    def test_admin_submission_confirmation(self):
        services.email_admin_submission_confirmation(proposal=self.proposal)
        self.assertIn(self.proposal.module.email, mail.outbox[0].to)
        self.assertIn(self.proposal.get_edit_url(), mail.outbox[0].alternatives[0][0])

    def test_tutor_completion(self):
        services.email_tutor_on_completion(proposal=self.proposal)
        self.assertIn(self.tutor_email, mail.outbox[0].to)
        self.assertIn(self.proposal.tutor.student.firstname, mail.outbox[0].body)
