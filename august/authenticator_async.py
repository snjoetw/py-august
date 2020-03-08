from datetime import datetime, timedelta, timezone
import json
import logging
import os

import aiofiles
from aiohttp import ClientError
from august.authenticator_common import (
    Authentication,
    AuthenticationState,
    AuthenticatorCommon,
    ValidationResult,
    from_authentication_json,
    to_authentication_json,
)

_LOGGER = logging.getLogger(__name__)


class AuthenticatorAsync(AuthenticatorCommon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def async_setup_authentication(self):
        access_token_cache_file = self._access_token_cache_file
        if access_token_cache_file is not None and os.path.exists(
            access_token_cache_file
        ):
            async with aiofiles.open(access_token_cache_file, "r") as file:
                try:
                    contents = await file.read()
                    self._authentication = from_authentication_json(json.loads(contents))

                    # If token is to expire within 7 days then print a warning.
                    if self._authentication.is_expired():
                        _LOGGER.error("Token has expired.")
                        self._authentication = Authentication(
                            AuthenticationState.REQUIRES_AUTHENTICATION,
                            install_id=self._install_id,
                        )
                    # If token is not expired but less then 7 days before it
                    # will.
                    elif (
                        self._authentication.parsed_expiration_time()
                        - datetime.now(timezone.utc)
                    ) < timedelta(days=7):
                        exp_time = self._authentication.access_token_expires
                        _LOGGER.warning(
                            "API Token is going to expire at %s "
                            "hours. Deleting file %s will result "
                            "in a new token being requested next"
                            " time",
                            exp_time,
                            access_token_cache_file,
                        )
                    return
                except json.decoder.JSONDecodeError as error:
                    _LOGGER.error(
                        "Unable to read cache file (%s): %s",
                        access_token_cache_file,
                        error,
                    )

        self._authentication = Authentication(
            AuthenticationState.REQUIRES_AUTHENTICATION, install_id=self._install_id
        )

    async def async_authenticate(self):
        if self._authentication.state == AuthenticationState.AUTHENTICATED:
            return self._authentication

        identifier = self._login_method + ":" + self._username
        install_id = self._authentication.install_id
        response = await self._api.async_get_session(
            install_id, identifier, self._password
        )

        json_dict = await response.json()
        authentication = self._authentication_from_session_response(
            install_id, response.headers, json_dict
        )

        if authentication.state == AuthenticationState.AUTHENTICATED:
            await self._async_cache_authentication(authentication)

        return authentication

    async def async_validate_verification_code(self, verification_code):
        if not verification_code:
            return ValidationResult.INVALID_VERIFICATION_CODE

        try:
            await self._api.async_validate_verification_code(
                self._authentication.access_token,
                self._login_method,
                self._username,
                verification_code,
            )
        except ClientError:
            return ValidationResult.INVALID_VERIFICATION_CODE

        return ValidationResult.VALIDATED

    async def async_send_verification_code(self):
        await self._api.async_send_verification_code(
            self._authentication.access_token, self._login_method, self._username
        )

        return True

    async def async_refresh_access_token(self, force=False):
        if not self.should_refresh() and not force:
            return self._authentication

        if self._authentication.state != AuthenticationState.AUTHENTICATED:
            _LOGGER.warning("Tried to refresh access token when not authenticated")
            return self._authentication

        refreshed_token = await self._api.async_refresh_access_token(
            self._authentication.access_token
        )

        authentication = self._process_refreshed_access_token(refreshed_token)
        await self._async_cache_authentication(authentication)
        return authentication

    async def _async_cache_authentication(self, authentication):
        if self._access_token_cache_file is not None:
            async with aiofiles.open(self._access_token_cache_file, "w") as file:
                await file.write(to_authentication_json(authentication))
