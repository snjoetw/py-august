import json
import logging
import os
import uuid
from enum import Enum

import requests

from august.api import HEADER_AUGUST_ACCESS_TOKEN

_LOGGER = logging.getLogger(__name__)


def to_authentication_json(authentication):
    if authentication is None:
        return json.dumps({})

    return json.dumps({
        "install_id": authentication.install_id,
        "access_token": authentication.access_token,
        "access_token_expires": authentication.access_token_expires,
        "state": authentication.state.value,
    })


def from_authentication_json(data):
    if data is None:
        return None

    install_id = data["install_id"]
    access_token = data["access_token"]
    access_token_expires = data["access_token_expires"]
    state = AuthenticationState(data["state"])
    return Authentication(state, install_id, access_token,
                          access_token_expires)


class Authentication:
    def __init__(self, state, install_id=None, access_token=None,
                 access_token_expires=None):
        self._state = state
        self._install_id = str(
            uuid.uuid4()) if install_id is None else install_id
        self._access_token = access_token
        self._access_token_expires = access_token_expires

    @property
    def install_id(self):
        return self._install_id

    @property
    def access_token(self):
        return self._access_token

    @property
    def access_token_expires(self):
        return self._access_token_expires

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value


class AuthenticationState(Enum):
    REQUIRES_AUTHENTICATION = "requires_authentication"
    REQUIRES_VALIDATION = "requires_validation"
    AUTHENTICATED = "authenticated"
    BAD_PASSWORD = "bad_password"


class ValidationResult(Enum):
    VALIDATED = "validated"
    INVALID_VERIFICATION_CODE = "invalid_verification_code"


class Authenticator:
    def __init__(self, api, login_method, username, password, install_id=None,
                 access_token_cache_file=None):
        self._api = api
        self._login_method = login_method
        self._username = username
        self._password = password
        self._access_token_cache_file = access_token_cache_file

        if (access_token_cache_file is not None and
                os.path.exists(access_token_cache_file)):
            with open(access_token_cache_file, 'r') as file:
                try:
                    self._authentication = from_authentication_json(
                        json.load(file))
                    return
                except json.decoder.JSONDecodeError as error:
                    _LOGGER.error("Unable to read cache file (%s): %s",
                                  access_token_cache_file, error)

        self._authentication = Authentication(
            AuthenticationState.REQUIRES_AUTHENTICATION,
            install_id=install_id)

    def authenticate(self):
        if self._authentication.state == AuthenticationState.AUTHENTICATED:
            return self._authentication

        identifier = self._login_method + ":" + self._username
        install_id = self._authentication.install_id
        response = self._api.get_session(install_id, identifier,
                                         self._password)

        data = response.json()
        access_token = response.headers[HEADER_AUGUST_ACCESS_TOKEN]
        access_token_expires = data["expiresAt"]
        v_password = data["vPassword"]
        v_install_id = data["vInstallId"]

        if not v_password:
            state = AuthenticationState.BAD_PASSWORD
        elif not v_install_id:
            state = AuthenticationState.REQUIRES_VALIDATION
        else:
            state = AuthenticationState.AUTHENTICATED

        self._authentication = Authentication(state, install_id, access_token,
                                              access_token_expires)

        if state == AuthenticationState.AUTHENTICATED:
            self._cache_authentication(self._authentication)

        return self._authentication

    def send_verification_code(self):
        self._api.send_verification_code(
            self._authentication.access_token, self._login_method,
            self._username)

        return True

    def validate_verification_code(self, verification_code):
        if not verification_code:
            return ValidationResult.INVALID_VERIFICATION_CODE

        try:
            self._api.validate_verification_code(
                self._authentication.access_token, self._login_method,
                self._username, verification_code)
        except requests.exceptions.RequestException:
            return ValidationResult.INVALID_VERIFICATION_CODE

        return ValidationResult.VALIDATED

    def _cache_authentication(self, authentication):
        if self._access_token_cache_file is not None:
            with open(self._access_token_cache_file, "w") as file:
                file.write(to_authentication_json(authentication))
