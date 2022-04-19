from dataclasses import dataclass
from datetime import date, time
from unittest import mock

from django import test
from django.urls import reverse

from apps.core.utils.tests import LoggedInViewTestMixin
from apps.module.models import Equipment, Room, RoomSetups
from apps.module.tests.factories import ModuleFactory

from .. import client, services

TEST_URL = 'http://cabs.test'


def mocked_requests_post(*args, **kwargs):
    """Mock the results we get back from requests.post(), with results for each api call"""

    @dataclass
    class MockResponse:
        json_data: dict
        status_code: int

        def json(self) -> dict:
            return self.json_data

    base_url = TEST_URL + '/Auth/auth/Token'
    api_return_values = {
        f'{base_url}/sign-in': MockResponse({'access_token': 'abcde'}, 200),
        f'{base_url}/api/CreateMbr': MockResponse({'outputParameters': {'result': 1, 'mbr_sysno': 'M000001'}}, 200),
        f'{base_url}/api/CreateSession': MockResponse({'outputParameters': {'next_num': 'S000001'}}, 200),
        f'{base_url}/api/CheckRoomAvailability': MockResponse({'returnValue': 1}, 200),
        f'{base_url}/api/BookRoom': MockResponse({'outputParameters': {'book_room_result': 'F000001'}}, 200),
        f'{base_url}/api/BookExtra': MockResponse({'returnValue': 1}, 200),
    }
    return api_return_values.get(args[0], MockResponse({}, 404))


@test.override_settings(CABS_API_URL=TEST_URL)
@mock.patch('requests.post', side_effect=mocked_requests_post)
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
        cls.module.equipment.add(Equipment.objects.create(name='Item'))
        cls.url = reverse('cabs_booking:module-booking', kwargs={'pk': cls.module.pk})

    def test_booking_stores_results_from_api(self, mocked_service: mock.MagicMock):
        """Check that the api runs, and we wind up with a correct booking record"""
        api_client = client.CABSApiClient()

        booking = services.create_module_bookings(module=self.module, api_client=api_client)

        self.assertEqual(booking.mbr_id, 'M000001')
        self.assertEqual(booking.confirmed, 9)  # 9 weeks between start and end dates
        self.assertEqual(booking.provisional, 0)
