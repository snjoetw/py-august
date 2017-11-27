# https://github.com/mlamoure/Indigo-August-Home/blob/master/August%20Home.indigoPlugin/Contents/Server%20Plugin/plugin.py
import logging

import requests

from august.activity import DoorbellDingActivity, DoorbellMotionActivity, \
    DoorbellViewActivity
from august.doorbell import Doorbell

HEADER_ACCEPT_VERSION = "Accept-Version"
HEADER_AUGUST_ACCESS_TOKEN = "x-august-access-token"
HEADER_AUGUST_API_KEY = "x-august-api-key"
HEADER_KEASE_API_KEY = "x-kease-api-key"
HEADER_CONTENT_TYPE = "Content-Type"
HEADER_USER_AGENT = "User-Agent"

HEADER_VALUE_API_KEY = "727dba56-fe45-498d-b4aa-293f96aae0e5"
HEADER_VALUE_CONTENT_TYPE = "application/json"
HEADER_VALUE_USER_AGENT = "August/Luna-3.2.2"
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
API_GET_LOCKS_URL = API_BASE_URL + "/users/locks/mine"
API_GET_LOCK_URL = API_BASE_URL + "/locks/{lock_id}"
API_GET_LOCK_STATUS_URL = API_BASE_URL + "/locks/{lock_id}/status"

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


class Api:
    def __init__(self, timeout=10):
        self._timeout = timeout

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

        return [Doorbell(data) for data in json.values()]

    def get_doorbell(self, access_token, doorbell_id):
        response = self._call_api(
            "get",
            API_GET_DOORBELL_URL.format(doorbell_id=doorbell_id),
            access_token=access_token)

        return response.json()

    def get_locks(self, access_token):
        response = self._call_api(
            "get",
            API_GET_LOCKS_URL,
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

            if action in ["doorbell_call_missed", "doorbell_call_hangup"]:
                activities.append(DoorbellDingActivity(activity_json))
            elif action == "doorbell_motion_detected":
                activities.append(DoorbellMotionActivity(activity_json))
            elif action == "doorbell_call_initiated":
                activities.append(DoorbellViewActivity(activity_json))

        return activities

    def get_lock(self, access_token, lock_id):
        response = self._call_api(
            "get",
            API_GET_LOCK_URL.format(lock_id=lock_id),
            access_token=access_token)

        return response.json()

    def get_lock_status(self, access_token, lock_id):
        response = self._call_api(
            "get",
            API_GET_LOCK_STATUS_URL.format(lock_id=lock_id),
            access_token=access_token)

        return response.json()

    def wakeup_doorbell(self, access_token, doorbell_id):
        self._call_api(
            "put",
            API_WAKEUP_DOORBELL_URL.format(doorbell_id=doorbell_id),
            access_token=access_token)

        return True

    def _call_api(self, method, url, access_token=None, **kwargs):
        payload = kwargs.get("params") or kwargs.get("json")

        if "headers" not in kwargs:
            kwargs["headers"] = _api_headers(access_token=access_token)

        _LOGGER.debug("About to call %s with header=%s and payload=%s", url,
                      kwargs["headers"], payload)

        response = requests.request(method, url, timeout=self._timeout,
                                    **kwargs)

        _LOGGER.debug("Received API response: %s, %s", response.status_code,
                      response.content)

        response.raise_for_status()
        return response
