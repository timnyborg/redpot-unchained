from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import TestCase

from ..models import Fee, FeeTypes
from . import factories


class TestFeeViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.module = factories.ModuleFactory()
        cls.fee = factories.FeeFactory(module=cls.module)
        cls.create_url = reverse('fee:new', args=[cls.module.pk])
        cls.edit_url = reverse('fee:edit', args=[cls.fee.pk])

    def setUp(self):
        self.client.force_login(self.user)

    def test_get_create(self):
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)

    def test_post_create(self):
        response = self.client.post(
            self.create_url,
            data={
                'description': 'Test fee',
                'amount': 200.00,
                'type': FeeTypes.PROGRAMME,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Fee.objects.last().amount, 200.00)

    def test_get_edit(self):
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)

    def test_post_edit(self):
        response = self.client.post(
            self.edit_url,
            data={
                'description': self.fee.description,
                'amount': 200.00,
                'type': self.fee.type_id,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Fee.objects.last().amount, 200.00)
