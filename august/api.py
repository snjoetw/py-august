import logging
import time

from requests import Session, request

from august.activity import (ACTIVITY_ACTIONS_DOOR_OPERATION,
                             ACTIVITY_ACTIONS_DOORBELL_DING,
                             ACTIVITY_ACTIONS_DOORBELL_MOTION,
                             ACTIVITY_ACTIONS_DOORBELL_VIEW,
                             ACTIVITY_ACTIONS_LOCK_OPERATION,
                             DoorbellDingActivity, DoorbellMotionActivity,
                             DoorbellViewActivity, DoorOperationActivity,
                             LockOperationActivity)
from august.doorbell import Doorbell, DoorbellDetail
from august.lock import Lock, LockDetail, LockDoorStatus, LockStatus
from august.pin import Pin

HEADER_ACCEPT_VERSION = "Accept-Version"
HEADER_AUGUST_ACCESS_TOKEN = "x-august-access-token"
HEADER_AUGUST_API_KEY = "x-august-api-key"
HEADER_KEASE_API_KEY = "x-kease-api-key"
HEADER_CONTENT_TYPE = "Content-Type"
HEADER_USER_AGENT = "User-Agent"

HEADER_VALUE_API_KEY = "79fd0eb6-381d-4adf-95a0-47721289d1d9"
HEADER_VALUE_CONTENT_TYPE = "application/json"
HEADER_VALUE_USER_AGENT = "August/2019.12.16.4708 CFNetwork/1121.2.2 Darwin/19.3.0"
HEADER_VALUE_ACCEPT_VERSION = "0.0.1"

API_BASE_URL = "https://api-production.august.com"
API_GET_SESSION_URL = API_BASE_URL + "/session"
API_SEND_VERIFICATION_CODE_URLS = {
    "phone": API_BASE_URL + "/validation/phone",
    "email": API_BASE_URL + "/validation/email",
}
API_VALIDATE_VERIFICATION_CODE_URLS = {
    "phone": API_BASE_URL + "/validate/phone",
    "email": API_BASE_URL + "/validate/email",
}
API_GET_HOUSE_ACTIVITIES_URL = API_BASE_URL + "/houses/{house_id}/activities"
API_GET_DOORBELLS_URL = API_BASE_URL + "/users/doorbells/mine"
API_GET_DOORBELL_URL = API_BASE_URL + "/doorbells/{doorbell_id}"
API_WAKEUP_DOORBELL_URL = API_BASE_URL + "/doorbells/{doorbell_id}/wakeup"
API_GET_HOUSES_URL = API_BASE_URL + "/users/houses/mine"
API_GET_HOUSE_URL = API_BASE_URL + "/houses/{house_id}"
API_GET_LOCKS_URL = API_BASE_URL + "/users/locks/mine"
API_GET_LOCK_URL = API_BASE_URL + "/locks/{lock_id}"
API_GET_LOCK_STATUS_URL = API_BASE_URL + "/locks/{lock_id}/status"
API_GET_PINS_URL = API_BASE_URL + "/locks/{lock_id}/pins"
API_LOCK_URL = API_BASE_URL + "/remoteoperate/{lock_id}/lock"
API_UNLOCK_URL = API_BASE_URL + "/remoteoperate/{lock_id}/unlock"

_LOGGER = logging.getLogger(__name__)


def _api_headers(access_token=None):
    headers = {
        HEADER_ACCEPT_VERSION: HEADER_VALUE_ACCEPT_VERSION,
        HEADER_AUGUST_API_KEY: HEADER_VALUE_API_KEY,
        HEADER_KEASE_API_KEY: HEADER_VALUE_API_KEY,
        HEADER_CONTENT_TYPE: HEADER_VALUE_CONTENT_TYPE,
        HEADER_USER_AGENT: HEADER_VALUE_USER_AGENT,
    }

    if access_token:
        headers[HEADER_AUGUST_ACCESS_TOKEN] = access_token

    return headers


LOCKED_STATUS = ("locked", "kAugLockState_Locked")
UNLOCKED_STATUS = ("unlocked", "kAugLockState_Unlocked")
CLOSED_STATUS = ("closed", "kAugLockDoorState_Closed")
OPEN_STATUS = ("open", "kAugLockDoorState_Open")


def _determine_lock_status(status):
    if status in LOCKED_STATUS:
        return LockStatus.LOCKED
    if status in UNLOCKED_STATUS:
        return LockStatus.UNLOCKED
    return LockStatus.UNKNOWN


def _determine_lock_door_status(status):
    if status in CLOSED_STATUS:
        return LockDoorStatus.CLOSED
    if status in OPEN_STATUS:
        return LockDoorStatus.OPEN
    return LockDoorStatus.UNKNOWN


class Api:
    def __init__(self, timeout=10, command_timeout=60,
                 http_session: Session = None):
        self._timeout = timeout
        self._command_timeout = command_timeout
        self._http_session = http_session

    def get_session(self, install_id, identifier, password):
        response = self._call_api(
            "post",
            API_GET_SESSION_URL,
            json={
                "installId": install_id,
                "identifier": identifier,
                "password": password,
            })

        return response

    def send_verification_code(self, access_token, login_method, username):
        response = self._call_api(
            "post",
            API_SEND_VERIFICATION_CODE_URLS[login_method],
            access_token=access_token,
            json={
                "value": username
            })

        return response

    def validate_verification_code(self, access_token, login_method, username,
                                   verification_code):
        response = self._call_api(
            "post",
            API_VALIDATE_VERIFICATION_CODE_URLS[login_method],
            access_token=access_token,
            json={
                login_method: username,
                "code": str(verification_code)
            })

        return response

    def get_doorbells(self, access_token):
        json = self._call_api(
            "get",
            API_GET_DOORBELLS_URL,
            access_token=access_token).json()

        return [Doorbell(device_id, data) for device_id, data in json.items()]

    def get_doorbell_detail(self, access_token, doorbell_id):
        response = self._call_api(
            "get",
            API_GET_DOORBELL_URL.format(doorbell_id=doorbell_id),
            access_token=access_token)

        return DoorbellDetail(response.json())

    def wakeup_doorbell(self, access_token, doorbell_id):
        self._call_api(
            "put",
            API_WAKEUP_DOORBELL_URL.format(doorbell_id=doorbell_id),
            access_token=access_token)

        return True

    def get_houses(self, access_token):
        response = self._call_api(
            "get",
            API_GET_HOUSES_URL,
            access_token=access_token)

        return response.json()

    def get_house(self, access_token, house_id):
        response = self._call_api(
            "get",
            API_GET_HOUSE_URL.format(house_id=house_id),
            access_token=access_token)

        return response.json()

    def get_house_activities(self, access_token, house_id, limit=8):
        response = self._call_api(
            "get",
            API_GET_HOUSE_ACTIVITIES_URL.format(house_id=house_id),
            access_token=access_token,
            params={
                "limit": limit,
            })

        activities = []
        for activity_json in response.json():
            action = activity_json.get("action")

            if action in ACTIVITY_ACTIONS_DOORBELL_DING:
                activities.append(DoorbellDingActivity(activity_json))
            elif action in ACTIVITY_ACTIONS_DOORBELL_MOTION:
                activities.append(DoorbellMotionActivity(activity_json))
            elif action in ACTIVITY_ACTIONS_DOORBELL_VIEW:
                activities.append(DoorbellViewActivity(activity_json))
            elif action in ACTIVITY_ACTIONS_LOCK_OPERATION:
                activities.append(LockOperationActivity(activity_json))
            elif action in ACTIVITY_ACTIONS_DOOR_OPERATION:
                activities.append(DoorOperationActivity(activity_json))

        return activities

    def get_locks(self, access_token):
        json = self._call_api(
            "get",
            API_GET_LOCKS_URL,
            access_token=access_token).json()

        return [Lock(device_id, data) for device_id, data in json.items()]

    def get_operable_locks(self, access_token):
        locks = self.get_locks(access_token)

        return [lock for lock in locks if lock.is_operable]

    def get_lock_detail(self, access_token, lock_id):
        response = self._call_api(
            "get",
            API_GET_LOCK_URL.format(lock_id=lock_id),
            access_token=access_token)

        return LockDetail(response.json())

    def get_lock_status(self, access_token, lock_id, door_status=False):
        json = self._call_api(
            "get",
            API_GET_LOCK_STATUS_URL.format(lock_id=lock_id),
            access_token=access_token).json()

        if door_status:
            return (_determine_lock_status(json.get("status")),
                    _determine_lock_door_status(json.get("doorState")))

        return _determine_lock_status(json.get("status"))

    def get_lock_door_status(self, access_token, lock_id, lock_status=False):
        json = self._call_api(
            "get",
            API_GET_LOCK_STATUS_URL.format(lock_id=lock_id),
            access_token=access_token).json()

        if lock_status:
            return (_determine_lock_door_status(json.get("doorState")),
                    _determine_lock_status(json.get("status")))

        return _determine_lock_door_status(json.get("doorState"))

    def get_pins(self, access_token, lock_id):
        json = self._call_api(
            "get",
            API_GET_PINS_URL.format(lock_id=lock_id),
            access_token=access_token
        ).json()

        return [Pin(pin_json) for pin_json in json.get('loaded', [])]

    def lock(self, access_token, lock_id):
        json = self._call_api(
            "put",
            API_LOCK_URL.format(lock_id=lock_id),
            access_token=access_token,
            timeout=self._command_timeout).json()

        return _determine_lock_status(json.get("status"))

    def unlock(self, access_token, lock_id):
        json = self._call_api(
            "put",
            API_UNLOCK_URL.format(lock_id=lock_id),
            access_token=access_token,
            timeout=self._command_timeout).json()

        return _determine_lock_status(json.get("status"))

    def refresh_access_token(self, access_token):
        response = self._call_api(
            "get",
            API_GET_HOUSES_URL,
            access_token=access_token)

        return response.headers[HEADER_AUGUST_ACCESS_TOKEN]

    def _call_api(self, method, url, access_token=None, **kwargs):
        payload = kwargs.get("params") or kwargs.get("json")

        if "headers" not in kwargs:
            kwargs["headers"] = _api_headers(access_token=access_token)

        if "timeout" not in kwargs:
            kwargs["timeout"] = self._timeout

        _LOGGER.debug("About to call %s with header=%s and payload=%s", url,
                      kwargs["headers"], payload)

        attempts = 0
        while attempts < 10:
            attempts += 1
            response = self._http_session.request(method, url, **kwargs) if \
                self._http_session is not None else \
                request(method, url, **kwargs)
            _LOGGER.debug("Received API response: %s, %s",
                          response.status_code,
                          response.content)
            if response.status_code == 429:
                _LOGGER.debug(
                    "August sent a 429 (attempt: %d), sleeping and trying again",
                    attempts)
                time.sleep(2.5)
                continue
            break

        response.raise_for_status()
        return response
