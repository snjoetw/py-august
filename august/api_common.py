"""Api functions common between sync and async."""

import dateutil.parser
from august.activity import (
    ACTIVITY_ACTIONS_DOOR_OPERATION,
    ACTIVITY_ACTIONS_DOORBELL_DING,
    ACTIVITY_ACTIONS_DOORBELL_MOTION,
    ACTIVITY_ACTIONS_DOORBELL_VIEW,
    ACTIVITY_ACTIONS_LOCK_OPERATION,
    DoorbellDingActivity,
    DoorbellMotionActivity,
    DoorbellViewActivity,
    DoorOperationActivity,
    LockOperationActivity,
)
from august.doorbell import Doorbell
from august.lock import Lock, LockDoorStatus, determine_door_state, door_state_to_string

API_RETRY_TIME = 2.5
API_RETRY_ATTEMPTS = 10

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


def _convert_lock_result_to_activities(lock_json_dict):
    activities = []
    lock_info_json_dict = lock_json_dict.get("info", {})
    lock_id = lock_info_json_dict.get("lockID")
    lock_action_text = lock_info_json_dict.get("action")
    activity_epoch = _datetime_string_to_epoch(lock_info_json_dict.get("startTime"))
    activity_lock_dict = _map_lock_result_to_activity(
        lock_id, activity_epoch, lock_action_text
    )
    activities.append(activity_lock_dict)

    door_state = determine_door_state(lock_json_dict.get("doorState"))
    if door_state != LockDoorStatus.UNKNOWN:
        activity_door_dict = _map_lock_result_to_activity(
            lock_id, activity_epoch, door_state_to_string(door_state)
        )
        activities.append(activity_door_dict)

    return activities


def _activity_from_dict(activity_dict):
    action = activity_dict.get("action")

    if action in ACTIVITY_ACTIONS_DOORBELL_DING:
        return DoorbellDingActivity(activity_dict)
    if action in ACTIVITY_ACTIONS_DOORBELL_MOTION:
        return DoorbellMotionActivity(activity_dict)
    if action in ACTIVITY_ACTIONS_DOORBELL_VIEW:
        return DoorbellViewActivity(activity_dict)
    if action in ACTIVITY_ACTIONS_LOCK_OPERATION:
        return LockOperationActivity(activity_dict)
    if action in ACTIVITY_ACTIONS_DOOR_OPERATION:
        return DoorOperationActivity(activity_dict)
    return None


def _map_lock_result_to_activity(lock_id, activity_epoch, action_text):
    """Create an august activity from a lock result."""
    mapped_dict = {
        "dateTime": activity_epoch,
        "deviceID": lock_id,
        "deviceType": "lock",
        "action": action_text,
    }
    return _activity_from_dict(mapped_dict)


def _datetime_string_to_epoch(datetime_string):
    return dateutil.parser.parse(datetime_string).timestamp() * 1000


def _process_activity_json(json_dict):
    activities = []
    for activity_json in json_dict:
        activity = _activity_from_dict(activity_json)
        if activity:
            activities.append(activity)

    return activities


def _process_doorbells_json(json_dict):
    return [Doorbell(device_id, data) for device_id, data in json_dict.items()]


def _process_locks_json(json_dict):
    return [Lock(device_id, data) for device_id, data in json_dict.items()]


class ApiCommon:
    """Api dict shared between async and sync."""

    def _build_get_session_request(self, install_id, identifier, password):
        return {
            "method": "post",
            "url": API_GET_SESSION_URL,
            "json": {
                "installId": install_id,
                "identifier": identifier,
                "password": password,
            },
        }

    def _build_send_verification_code_request(
        self, access_token, login_method, username
    ):
        return {
            "method": "post",
            "url": API_SEND_VERIFICATION_CODE_URLS[login_method],
            "access_token": access_token,
            "json": {"value": username},
        }

    def _build_validate_verification_code_request(
        self, access_token, login_method, username, verification_code
    ):
        return {
            "method": "post",
            "url": API_VALIDATE_VERIFICATION_CODE_URLS[login_method],
            "access_token": access_token,
            "json": {login_method: username, "code": str(verification_code)},
        }

    def _build_get_doorbells_request(self, access_token):
        return {
            "method": "get",
            "url": API_GET_DOORBELLS_URL,
            "access_token": access_token,
        }

    def _build_get_doorbell_detail_request(self, access_token, doorbell_id):
        return {
            "method": "get",
            "url": API_GET_DOORBELL_URL.format(doorbell_id=doorbell_id),
            "access_token": access_token,
        }

    def _build_wakeup_doorbell_request(self, access_token, doorbell_id):
        return {
            "method": "put",
            "url": API_WAKEUP_DOORBELL_URL.format(doorbell_id=doorbell_id),
            "access_token": access_token,
        }

    def _build_get_houses_request(self, access_token):
        return {"method": "get", "access_token": access_token}

    def _build_get_house_request(self, access_token, house_id):
        return {
            "method": "get",
            "url": API_GET_HOUSE_URL.format(house_id=house_id),
            "access_token": access_token,
        }

    def _build_get_house_activities_request(self, access_token, house_id, limit=8):
        return {
            "method": "get",
            "url": API_GET_HOUSE_ACTIVITIES_URL.format(house_id=house_id),
            "access_token": access_token,
            "params": {"limit": limit},
        }

    def _build_get_locks_request(self, access_token):
        return {"method": "get", "url": API_GET_LOCKS_URL, "access_token": access_token}

    def _build_get_lock_detail_request(self, access_token, lock_id):
        return {
            "method": "get",
            "url": API_GET_LOCK_URL.format(lock_id=lock_id),
            "access_token": access_token,
        }

    def _build_get_lock_status_request(self, access_token, lock_id):
        return {
            "method": "get",
            "url": API_GET_LOCK_STATUS_URL.format(lock_id=lock_id),
            "access_token": access_token,
        }

    def _build_get_pins_request(self, access_token, lock_id):
        return {
            "method": "get",
            "url": API_GET_PINS_URL.format(lock_id=lock_id),
            "access_token": access_token,
        }

    def _build_refresh_access_token_request(self, access_token):
        return {
            "method": "get",
            "url": API_GET_HOUSES_URL,
            "access_token": access_token,
        }

    def _build_call_lock_operation_request(
        self, url_str, access_token, lock_id, timeout
    ):
        return {
            "method": "put",
            "url": url_str.format(lock_id=lock_id),
            "access_token": access_token,
            "timeout": timeout,
        }
