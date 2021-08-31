from decimal import Decimal

from parameterized import parameterized

from django import test
from django.contrib.auth.models import Permission
from django.contrib.messages import get_messages
from django.urls import reverse, reverse_lazy

from apps.core.utils.tests import LoggedInMixin, LoggedInViewTestMixin
from apps.enrolment.tests.factories import EnrolmentFactory

from .. import models
from . import factories


class TestApprove(LoggedInViewTestMixin, test.TestCase):
    url = reverse_lazy('amendment:approve')
    superuser = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.amendment = factories.AmendmentFactory(approver=cls.user)

    def test_get(self):
        """Check the datatable shows the assigned item"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['table'].rows), 1)

    def test_post(self):
        """Check posting correctly updates the item"""
        response = self.client.post(self.url, data={'amendment': [self.amendment.id]})
        self.assertEqual(response.status_code, 302)
        self.amendment.refresh_from_db()
        self.assertEqual(self.amendment.status_id, models.AmendmentStatuses.APPROVED)

    def test_empty_post(self):
        """Check posting nothing returns none updated message"""
        response = self.client.post(self.url, data={'amendment': []})
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('No requests', messages[0].message)


class TestDelete(LoggedInViewTestMixin, test.TestCase):
    superuser = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.amendment = factories.AmendmentFactory(approver=cls.user)
        cls.url = cls.amendment.get_delete_url()

    def test_post(self):
        """Check posting correctly deletes the item"""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(models.Amendment.DoesNotExist):
            self.amendment.refresh_from_db()


class TestEdit(LoggedInViewTestMixin, test.TestCase):
    superuser = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        permission = Permission.objects.get(content_type__app_label='amendment', codename='approve')
        cls.user.user_permissions.add(permission)
        cls.amendment = factories.AmendmentFactory(approver=cls.user)
        cls.url = cls.amendment.get_edit_url()

    @parameterized.expand(
        [
            ('amendment', models.AmendmentTypes.AMENDMENT),
            ('transfer', models.AmendmentTypes.TRANSFER),
            ('refund', models.AmendmentTypes.ONLINE_REFUND),
        ]
    )
    def test_get(self, name: str, amend_type: int):
        """Check all the form variants load"""
        self.amendment.type_id = amend_type
        self.amendment.save()
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_complete_post(self):
        """Check updating an amendment"""
        self.amendment.type_id = models.AmendmentTypes.AMENDMENT
        self.amendment.reason_id = 6  # todo: enum
        self.amendment.save()
        response = self.client.post(
            self.get_url(),
            data={
                'amount': Decimal(875),
                'is_complete': True,
                'enrolment': self.amendment.enrolment_id,
                'reason': self.amendment.reason_id,
                'narrative': self.amendment.narrative,
                'approver': self.amendment.approver,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.amendment.refresh_from_db()
        self.assertEqual(self.amendment.amount, Decimal(875))
        self.assertEqual(self.amendment.status_id, models.AmendmentStatuses.COMPLETE)


class TestCreate(LoggedInMixin, test.TestCase):
    superuser = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.enrolment = EnrolmentFactory()
        # Make the user selectable as an approver
        permission = Permission.objects.get(content_type__app_label='amendment', codename='approve')
        cls.user.user_permissions.add(permission)

    @parameterized.expand(
        [
            ('amendment', models.AmendmentTypes.AMENDMENT),
            ('transfer', models.AmendmentTypes.TRANSFER),
            ('refund', models.AmendmentTypes.ONLINE_REFUND),
        ]
    )
    def test_get(self, name: str, amend_type: int):
        """Check all the form variants load"""
        url = reverse('amendment:new', args=[self.enrolment.id, amend_type])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_amendment_type_post(self):
        """Check updating an amendment"""
        url = reverse('amendment:new', args=[self.enrolment.id, models.AmendmentTypes.AMENDMENT])
        response = self.client.post(
            url,
            data={
                'amount': Decimal(875),
                'is_complete': True,
                'reason': 6,
                'narrative': 'Test',
                'approver': self.user,
            },
        )
        self.assertEqual(response.status_code, 302)
        amendment = models.Amendment.objects.last()
        self.assertEqual(amendment.amount, Decimal(875))
        self.assertEqual(amendment.status_id, models.AmendmentStatuses.RAISED)
