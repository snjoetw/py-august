"""Api calls for sync."""

import asyncio
import logging

from aiohttp import ClientResponseError
from august.api_common import (
    API_LOCK_URL,
    API_RETRY_ATTEMPTS,
    API_RETRY_TIME,
    API_UNLOCK_URL,
    HEADER_AUGUST_ACCESS_TOKEN,
    ApiCommon,
    _api_headers,
    _convert_lock_result_to_activities,
    _process_activity_json,
    _process_doorbells_json,
    _process_locks_json,
)
from august.doorbell import DoorbellDetail
from august.exceptions import AugustApiAIOHTTPError
from august.lock import LockDetail, determine_door_state, determine_lock_status
from august.pin import Pin

_LOGGER = logging.getLogger(__name__)


class ApiAsync(ApiCommon):
    def __init__(self, aiohttp_session, timeout=10, command_timeout=60):
        self._timeout = timeout
        self._command_timeout = command_timeout
        self._aiohttp_session = aiohttp_session

    async def async_get_session(self, install_id, identifier, password):
        return await self._async_dict_to_api(
            self._build_get_session_request(install_id, identifier, password)
        )

    async def async_send_verification_code(self, access_token, login_method, username):
        return await self._async_dict_to_api(
            self._build_send_verification_code_request(
                access_token, login_method, username
            )
        )

    async def async_validate_verification_code(
        self, access_token, login_method, username, verification_code
    ):
        return await self._async_dict_to_api(
            self._build_validate_verification_code_request(
                access_token, login_method, username, verification_code
            )
        )

    async def async_get_doorbells(self, access_token):
        response = await self._async_dict_to_api(
            self._build_get_doorbells_request(access_token)
        )
        return _process_doorbells_json(await response.json())

    async def async_get_doorbell_detail(self, access_token, doorbell_id):
        response = await self._async_dict_to_api(
            self._build_get_doorbell_detail_request(access_token, doorbell_id)
        )
        return DoorbellDetail(await response.json())

    async def async_wakeup_doorbell(self, access_token, doorbell_id):
        await self._async_dict_to_api(
            self._build_wakeup_doorbell_request(access_token, doorbell_id)
        )
        return True

    async def async_get_houses(self, access_token):
        return await self._async_dict_to_api(
            self._build_get_houses_request(access_token)
        )

    async def async_get_house(self, access_token, house_id):
        response = await self._async_dict_to_api(
            self._build_get_house_request(access_token, house_id)
        )
        return await response.json()

    async def async_get_house_activities(self, access_token, house_id, limit=8):
        response = await self._async_dict_to_api(
            self._build_get_house_activities_request(
                access_token, house_id, limit=limit
            )
        )
        return _process_activity_json(await response.json())

    async def async_get_locks(self, access_token):
        response = await self._async_dict_to_api(
            self._build_get_locks_request(access_token)
        )
        return _process_locks_json(await response.json())

    async def async_get_operable_locks(self, access_token):
        locks = await self.async_get_locks(access_token)

        return [lock for lock in locks if lock.is_operable]

    async def async_get_lock_detail(self, access_token, lock_id):
        response = await self._async_dict_to_api(
            self._build_get_lock_detail_request(access_token, lock_id)
        )
        return LockDetail(await response.json())

    async def async_get_lock_status(self, access_token, lock_id, door_status=False):
        response = await self._async_dict_to_api(
            self._build_get_lock_status_request(access_token, lock_id)
        )
        json_dict = await response.json()

        if door_status:
            return (
                determine_lock_status(json_dict.get("status")),
                determine_door_state(json_dict.get("doorState")),
            )

        return determine_lock_status(json_dict.get("status"))

    async def async_get_lock_door_status(
        self, access_token, lock_id, lock_status=False
    ):
        response = await self._async_dict_to_api(
            self._build_get_lock_status_request(access_token, lock_id)
        )
        json_dict = await response.json()

        if lock_status:
            return (
                determine_door_state(json_dict.get("doorState")),
                determine_lock_status(json_dict.get("status")),
            )

        return determine_door_state(json_dict.get("doorState"))

    async def async_get_pins(self, access_token, lock_id):
        response = await self._async_dict_to_api(
            self._build_get_pins_request(access_token, lock_id)
        )
        json_dict = await response.json()

        return [Pin(pin_json) for pin_json in json_dict.get("loaded", [])]

    async def _async_call_lock_operation(self, url_str, access_token, lock_id):
        response = await self._async_dict_to_api(
            self._build_call_lock_operation_request(
                url_str, access_token, lock_id, self._command_timeout
            )
        )
        return await response.json()

    async def _async_lock(self, access_token, lock_id):
        return await self._async_call_lock_operation(
            API_LOCK_URL, access_token, lock_id
        )

    async def async_lock(self, access_token, lock_id):
        """Execute a remote lock operation.

        Returns a LockStatus state.
        """
        return determine_lock_status(
            (await self._async_lock(access_token, lock_id)).get("status")
        )

    async def async_lock_return_activities(self, access_token, lock_id):
        """Execute a remote lock operation.

        Returns an array of one or more august.activity.Activity objects

        If the lock supports door sense one of the activities
        will include the current door state.
        """
        return _convert_lock_result_to_activities(
            await self._async_lock(access_token, lock_id)
        )

    async def _async_unlock(self, access_token, lock_id):
        return await self._async_call_lock_operation(
            API_UNLOCK_URL, access_token, lock_id
        )

    async def async_unlock(self, access_token, lock_id):
        """Execute a remote unlock operation.

        Returns a LockStatus state.
        """
        return determine_lock_status(
            (await self._async_unlock(access_token, lock_id)).get("status")
        )

    async def async_unlock_return_activities(self, access_token, lock_id):
        """Execute a remote lock operation.

        Returns an array of one or more august.activity.Activity objects

        If the lock supports door sense one of the activities
        will include the current door state.
        """
        return _convert_lock_result_to_activities(
            await self._async_unlock(access_token, lock_id)
        )

    async def async_refresh_access_token(self, access_token):
        """Obtain a new api token."""
        return (
            await self._async_dict_to_api(
                self._build_refresh_access_token_request(access_token)
            )
        ).headers[HEADER_AUGUST_ACCESS_TOKEN]

    async def _async_dict_to_api(self, api_dict):
        url = api_dict["url"]
        method = api_dict["method"]
        access_token = api_dict.get("access_token", None)
        del api_dict["url"]
        del api_dict["method"]
        if access_token:
            del api_dict["access_token"]

        payload = api_dict.get("params") or api_dict.get("json")

        if "headers" not in api_dict:
            api_dict["headers"] = _api_headers(access_token=access_token)

        if "timeout" not in api_dict:
            api_dict["timeout"] = self._timeout

        _LOGGER.debug(
            "About to call %s with header=%s and payload=%s",
            url,
            api_dict["headers"],
            payload,
        )

        attempts = 0
        while attempts < API_RETRY_ATTEMPTS:
            attempts += 1
            response = await self._aiohttp_session.request(method, url, **api_dict)
            _LOGGER.debug(
                "Received API response: %s, %s", response.status, await response.read()
            )
            if response.status == 429:
                _LOGGER.debug(
                    "August sent a 429 (attempt: %d), sleeping and trying again",
                    attempts,
                )
                asyncio.sleep(API_RETRY_TIME)
                continue
            break

        _raise_response_exceptions(response)

        return response


def _raise_response_exceptions(response):
    try:
        response.raise_for_status()
    except ClientResponseError as err:
        if err.status == 422:
            raise AugustApiAIOHTTPError(
                "The operation failed because the bridge (connect) is offline.",
            ) from err
        if err.status == 423:
            raise AugustApiAIOHTTPError(
                "The operation failed because the bridge (connect) is in use.",
            ) from err
        if err.status == 408:
            raise AugustApiAIOHTTPError(
                "The operation timed out because the bridge (connect) failed to respond.",
            ) from err
        raise err
