from datetime import datetime

from django import test
from django.core import mail

from apps.core.tests.factories import UserFactory
from apps.student.tests.factories import AddressFactory, EmailFactory
from apps.tutor.tests.factories import TutorFactory

from .. import services


class TestDetailsChangeEmail(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tutor = TutorFactory(created_on=datetime(1900, 1, 1), sortcode='123456')
        cls.address = AddressFactory(student=cls.tutor.student)
        EmailFactory(student=cls.tutor.student)
        cls.user = UserFactory.build()

    def test_tutor_changes(self):
        services.email_personnel_change(
            initial_values={'accountno': '800000', 'sortcode': ''},
            model=self.tutor,
            changed_data=['accountno', 'sortcode'],
            user=self.user,
        )
        self.assertEqual(len(mail.outbox), 2)
        # old values in email to personnel
        self.assertIn('800000', mail.outbox[0].body)
        # redacted sortcode in email to tutor
        self.assertIn('**-**-56', mail.outbox[1].body)

    def test_address_changes(self):
        services.email_personnel_change(
            initial_values={'line1': 'Flat 9'},
            model=self.address,
            changed_data=['line1'],
            user=self.user,
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Flat 9', mail.outbox[0].body)

    def test_name_changes(self):
        services.email_personnel_change(
            initial_values={'firstname': 'Greta'},
            model=self.tutor.student,
            changed_data=['firstname'],
            user=self.user,
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Greta', mail.outbox[0].body)

    def test_irrelevant_changes_do_not_send(self):
        services.email_personnel_change(
            initial_values={'qualifications': 'PhD'},
            model=self.tutor,
            changed_data=['qualifications'],
            user=self.user,
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_errors_on_bad_model_type(self):
        with self.assertRaises(TypeError):
            services.email_personnel_change(model=self.user, initial_values={}, changed_data=[], user=self.user)
