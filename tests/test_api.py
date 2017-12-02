import os
import unittest

import requests_mock

from august.api import API_GET_DOORBELLS_URL, Api, API_GET_LOCKS_URL, \
    API_GET_LOCK_STATUS_URL, API_LOCK_URL, API_UNLOCK_URL
from august.lock import LockStatus

ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9"


def load_fixture(filename):
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), 'fixtures', filename)
    with open(path) as fptr:
        return fptr.read()


class TestApi(unittest.TestCase):
    @requests_mock.Mocker()
    def test_get_doorbells(self, mock):
        mock.register_uri(
            "get",
            API_GET_DOORBELLS_URL,
            text=load_fixture("get_doorbells.json"))

        api = Api()
        doorbells = api.get_doorbells(ACCESS_TOKEN)

        self.assertEqual(2, len(doorbells))

        first = doorbells[0]
        self.assertEqual("K98GiDT45GUL", first.device_id)
        self.assertEqual("tBXZR0Z35E", first.serial_number)
        self.assertEqual("Front Door", first.device_name)
        self.assertEqual("doorbell_call_status_online", first.status)
        self.assertEqual(True, first.has_subscription)
        self.assertEqual("https://image.com/vmk16naaaa7ibuey7sar.jpg",
                         first.image_url)
        self.assertEqual("3dd2accaea08", first.house_id)

        second = doorbells[1]
        self.assertEqual("1KDAbJH89XYZ", second.device_id)
        self.assertEqual("aaaaR08888", second.serial_number)
        self.assertEqual("Back Door", second.device_name)
        self.assertEqual("doorbell_call_status_offline", second.status)
        self.assertEqual(False, second.has_subscription)
        self.assertEqual(None, second.image_url)
        self.assertEqual("3dd2accadddd", second.house_id)

    @requests_mock.Mocker()
    def test_get_locks(self, mock):
        mock.register_uri(
            "get",
            API_GET_LOCKS_URL,
            text=load_fixture("get_locks.json"))

        api = Api()
        locks = api.get_locks(ACCESS_TOKEN)

        self.assertEqual(1, len(locks))

        first = locks[0]
        self.assertEqual("A6697750D607098BAE8D6BAA11EF8063", first.device_id)
        self.assertEqual("Front Door Lock", first.device_name)
        self.assertEqual("000000000000", first.house_id)

    @requests_mock.Mocker()
    def test_get_lock_status_with_locked_response(self, mock):
        lock_id = 1234
        mock.register_uri(
            "get",
            API_GET_LOCK_STATUS_URL.format(lock_id=lock_id),
            text="{\"status\": \"kAugLockState_Locked\"}")

        api = Api()
        status = api.get_lock_status(ACCESS_TOKEN, lock_id)

        self.assertEqual(LockStatus.LOCKED, status)

    @requests_mock.Mocker()
    def test_get_lock_status_with_unlocked_response(self, mock):
        lock_id = 1234
        mock.register_uri(
            "get",
            API_GET_LOCK_STATUS_URL.format(lock_id=lock_id),
            text="{\"status\": \"kAugLockState_Unlocked\"}")

        api = Api()
        status = api.get_lock_status(ACCESS_TOKEN, lock_id)

        self.assertEqual(LockStatus.UNLOCKED, status)

    @requests_mock.Mocker()
    def test_lock(self, mock):
        lock_id = 1234
        mock.register_uri(
            "put",
            API_LOCK_URL.format(lock_id=lock_id),
            text="{\"status\": \"kAugLockState_Locked\"}")

        api = Api()
        status = api.lock(ACCESS_TOKEN, lock_id)

        self.assertEqual(LockStatus.LOCKED, status)

    @requests_mock.Mocker()
    def test_unlock(self, mock):
        lock_id = 1234
        mock.register_uri(
            "put",
            API_UNLOCK_URL.format(lock_id=lock_id),
            text="{\"status\": \"kAugLockState_Unlocked\"}")

        api = Api()
        status = api.unlock(ACCESS_TOKEN, lock_id)

        self.assertEqual(LockStatus.UNLOCKED, status)
