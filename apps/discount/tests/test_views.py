from datetime import datetime

import factory.django
from freezegun import freeze_time

from django import test
from django.urls import reverse_lazy

from apps.core.utils.tests import LoggedInMixin, LoggedInViewTestMixin

from .. import models


class DiscountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Discount

    name = factory.Sequence(lambda pk: f'Discount {pk}')
    code = factory.Faker('pystr', min_chars=6, max_chars=20)
    percent = factory.Faker('pyint', min_value=1, max_value=100)
    module_mask = 'O%'


class TestCreate(LoggedInViewTestMixin, test.TestCase):
    superuser = True
    url = reverse_lazy('discount:new')

    def test_post(self):
        response = self.client.post(
            self.url, {'name': 'Discount', 'code': 'DISCWORLD', 'percent': 50, 'module_mask': 'O%'}
        )
        self.assertEqual(response.status_code, 302)
        discount = models.Discount.objects.last()
        self.assertEqual(discount.code, 'DISCWORLD')


class TestEdit(LoggedInViewTestMixin, test.TestCase):
    superuser = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.discount = DiscountFactory()
        cls.url = cls.discount.get_edit_url()

    def test_post(self):
        response = self.client.post(
            self.url,
            {
                'name': 'Updatedname',
                'code': self.discount.code,
                'percent': 50,
                'module_mask': self.discount.module_mask,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.discount.refresh_from_db()
        self.assertEqual(self.discount.name, 'Updatedname')
        self.assertEqual(self.discount.percent, 50)


@freeze_time(datetime(2020, 1, 1))
class TestSearch(LoggedInMixin, test.TestCase):
    superuser = True
    url = reverse_lazy('discount:search')

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.expired_discount = DiscountFactory(expires_on=datetime(2000, 1, 1))

    def test_include_expired(self):
        response = self.client.get(self.url, data={'include_expired': True})
        self.assertContains(response, self.expired_discount.code)

    def test_exclude_expired(self):
        response = self.client.get(self.url, data={'include_expired': False})
        self.assertNotContains(response, self.expired_discount.code)
