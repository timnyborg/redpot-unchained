import random
import sys
from functools import partial
from typing import Callable

import requests

from django.conf import settings


class JSONRPCError(Exception):
    """Indicates an error reported by the rpc server"""


class APIClient:
    def __init__(self):
        self.url = settings.RP_API_URL
        if not self.url:
            raise ValueError('Cannot initialize rp_api client: RP_API_URL must be set')

    def call(self, *, method: str, **kwargs) -> dict:
        request_id = random.randint(0, sys.maxsize)
        payload = {
            "method": method,
            "params": kwargs,
            "id": request_id,
            "jsonrpc": "2.0",
        }
        response = requests.post(self.url, json=payload).json()

        if response.get('error'):
            raise JSONRPCError(response['error']['message'])
        if response.get('id') != request_id:
            raise JSONRPCError("jsonrpc request id mismatch")
        return response.get('result', {})

    def __getattr__(self, item) -> Callable:
        return partial(self.call, method=item)
