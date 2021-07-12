from django import test
from django.urls import reverse

from apps.core.utils.tests import LoggedInViewTestMixin
from apps.student.tests.factories import StudentFactory

from .. import models


class TestCreatePayment(LoggedInViewTestMixin, test.TestCase):
    @classmethod
    def extra_test_data(cls):
        cls.student = StudentFactory()
        cls.url = reverse('website_account:create', args=[cls.student.pk])

    def test_create(self):
        response = self.client.post(
            self.url,
            data={'username': 'test@test.net'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            models.WebsiteAccount.objects.last().student_id,
            self.student.id,
        )


class TestEditPayment(LoggedInViewTestMixin, test.TestCase):
    @classmethod
    def extra_test_data(cls):
        cls.account = models.WebsiteAccount.objects.create(
            student=StudentFactory(),
        )
        cls.url = reverse('website_account:edit', args=[cls.account.pk])

    def test_password_removed_without_permission(self):
        """Without superuser or permission, the password field shouldn't display"""
        response = self.client.get(self.url)
        self.assertNotIn(
            'new_password',
            response.context['form'].fields,
        )

    def test_update(self):
        # superuser ensures permission to edit password
        self.user.is_superuser = True
        self.user.save()
        response = self.client.post(
            self.url,
            data={
                'username': 'test@test.net',
                'new_password': 'qwer1234qwer',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.account.refresh_from_db()
        self.assertEqual(self.account.username, 'test@test.net')
        self.assertTrue(self.account.password.startswith('pbkdf'))
