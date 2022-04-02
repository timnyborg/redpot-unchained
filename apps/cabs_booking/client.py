from datetime import date, datetime, time
from functools import lru_cache

import requests

from django.conf import settings
from django.utils import timezone

SIGNIN_URL = settings.CABS_API_URL + '/Auth/auth/Token/sign-in'
CALL_URL = settings.CABS_API_URL + '/Auth/auth/Token/api/'


class CABSApiError(Exception):
    """Reports non-200 statuses from the API, or unexpected results"""


class CABSApiClient:
    @property
    @lru_cache
    def access_token(self) -> str:
        response = requests.post(
            SIGNIN_URL,
            json=settings.CABS_API_CREDENTIALS,
            headers={'Content-type': 'application/json'},
        )
        if response.status_code == 200:
            return response.json()['access_token']
        raise CABSApiError(f'CABS authentication failed: {response.status_code}: {response.reason}')

    def _call(self, endpoint: str, data: dict) -> dict:
        call_url = CALL_URL + endpoint
        response = requests.post(
            call_url,
            json=data,
            headers={'Content-type': 'application/json', 'Authorization': f'Bearer {self.access_token}'},
        )
        if response.status_code == 200:
            return response.json()
        raise CABSApiError(f'{response.status_code}: {response.reason}')

    @staticmethod
    def utc_datetime(dt: datetime) -> str:
        """Take a datetime and return a string of the UTC datetime"""
        # Add local timezone data, then convert to UTC
        dt = timezone.get_default_timezone().localize(dt).astimezone(timezone.utc)
        # Return an API-compatible string
        return dt.strftime('%Y-%m-%d %H:%M')

    # Endpoints
    def create_mbr(
        self,
        *,
        title: str,
        address_1: str = '',
        address_2: str = '',
        address_3: str = '',
        address_4: str = '',
        postcode: str = '',
        phone: str = '',
        email: str = '',
    ) -> str:
        data = {
            'mbr_company': title,
            'mbr_addr1': address_1,
            'mbr_addr2': address_2,
            'mbr_addr3': address_3,
            'mbr_addr4': address_4,
            'mbr_pcode': postcode,
            'mbr_phax1': phone,
            'mbr_phax2': '',
            'mbr_email': email,
            'mbr_internal': 0,
            'mbr_status': 'CONFRM',
            'mbr_sysno': '',
            'result': 0,
        }

        result = self._call('CreateMbr', data)
        if result['outputParameters']['result'] == 1:
            return result['outputParameters']['mbr_sysno']
        raise CABSApiError('Failed to create MBR')

    def create_session(self) -> str:
        result = self._call('CreateSession', {'next_num': ''})
        return result['outputParameters']['next_num']

    def check_room_availability(
        self,
        *,
        starting_at: datetime,
        ending_at: datetime,
        room_code: str,
        setup_minutes: int = 0,
    ) -> bool:
        data = {
            'Func_ref': '',
            'Book_StartDateTime': self.utc_datetime(dt=starting_at),
            'Book_EndDateTime': self.utc_datetime(dt=ending_at),
            'Book_Room': room_code,
            'Book_Setup': time(0, setup_minutes).strftime('%H:%M'),
            'Book_Bdown': time(0, setup_minutes).strftime('%H:%M'),
        }
        result = self._call('CheckRoomAvailability', data)
        return result['returnValue'] == 1  # This call has 1 = Available, -2 = unavailable

    def book_room(
        self,
        *,
        mbr: str,
        start_date: date,
        start_time: time,
        end_time: time,
        room_code: str,
        status: str,  # CONFRM or ANNCOM
        room_setup: str,
        max_size: int,
        tutor_name: str,
        session_id: str,
    ) -> str:
        data = {
            'Func_ref': '',
            'host_hr_id': mbr,
            'book_day': start_date.strftime('%Y-%m-%d'),
            'book_start': start_time.strftime('%H:%M'),
            'book_end': end_time.strftime('%H:%M'),
            'book_room': room_code,
            'book_status': status,
            'book_use': room_setup,
            'book_covers': max_size,
            'book_max': max_size,
            'book_min': max_size,
            'book_forecast': max_size,
            'book_cback': '',
            'book_credit': '',
            'book_matter': '',
            'sender_hr_id': 'leave this blank',
            'booked_id': 'Redpot',
            'book_purpose': tutor_name,
            'book_internal': 1,
            'book_sessno': session_id,
            'f_startdatetime': self.utc_datetime(datetime.combine(start_date, start_time)),
            'f_enddatetime': self.utc_datetime(datetime.combine(start_date, end_time)),
            'client_func': 0,
            'book_room_result': '',
        }
        result = self._call('BookRoom', data)

        return result['outputParameters']['book_room_result']

    def add_extra(
        self,
        *,
        room_sysno: str,
        start_date: date,
        start_time: time,
        end_time: time,
        note: str,
        extra_code: str,
    ) -> bool:
        data = {
            'AiPrikey': '',
            'func_ref': room_sysno,
            'extra_time': start_time.strftime('%H:%M'),
            'extra_covers': 1,
            'extra_notes': note,
            'booked_id': 'Redpot',
            'extra_code': extra_code,
            'extra_endtime': end_time.strftime('%H:%M'),
            'extra_charge': 0,
            'extra_cback': '',
            'extra_credit': '',
            'extra_canpost': 'No',
            'ExtraStartDateTime': self.utc_datetime(datetime.combine(start_date, start_time)),
            'ExtraEndDateTime': self.utc_datetime(datetime.combine(start_date, start_time)),
            'callingContext': 'Redpot',
        }

        result = self._call('BookExtra', data)

        return result['returnValue'] > 0
