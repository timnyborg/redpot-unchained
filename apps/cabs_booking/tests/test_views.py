import uuid
from datetime import date, time
from unittest import mock

from freezegun import freeze_time

from django import test
from django.urls import reverse

from apps.core.utils.tests import LoggedInViewTestMixin
from apps.module.models import Room, RoomSetups
from apps.module.tests.factories import ModuleFactory

from .. import services, tasks


@mock.patch.object(services, 'create_module_bookings')
class TestCreateModuleBookings(LoggedInViewTestMixin, test.TestCase):
    superuser = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.module = ModuleFactory(
            start_date=date(2020, 1, 1),
            end_date=date(2020, 3, 1),
            start_time=time(12),
            end_time=time(14),
            room_id=Room.objects.create(id='LR1', size=10),
            room_setup=RoomSetups.SEMINR,
        )
        cls.url = reverse('cabs_booking:module-booking', kwargs={'pk': cls.module.pk})

    def test_calls_service(self, mocked_service: mock.MagicMock):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)
        mocked_service.assert_called_once_with(module=self.module)

    def test_validation(self, mocked_service: mock.MagicMock):
        self.module.start_time = None
        self.module.save()

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        mocked_service.assert_not_called()


@freeze_time(date(2020, 1, 1))
@mock.patch.object(tasks.batch_cabs_module_bookings, 'delay', return_value=mock.Mock(id=uuid.uuid4()))
class TestAnnualWeeklyClassBookings(LoggedInViewTestMixin, test.TestCase):
    superuser = True
    url = reverse('cabs_booking:annual-booking')

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.module = ModuleFactory(
            start_date=date(2021, 1, 1),
            end_date=date(2021, 3, 1),
            start_time=time(12),
            end_time=time(14),
            room_id=Room.objects.create(id='LR1', size=10),
            room_setup=RoomSetups.SEMINR,
            portfolio_id=32,
        )

    def test_queues_task(self, mocked_task: mock.MagicMock):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)
        mocked_task.assert_called_once_with(module_ids=[self.module.id])

    def test_ignores_past(self, mocked_task: mock.MagicMock):
        self.module.start_date = date(2000, 1, 1)
        self.module.save()

        self.client.post(self.url)

        mocked_task.assert_called_once_with(module_ids=[])
