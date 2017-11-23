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
        return json.dump({})

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
    NONE = "none"
    REQUIRES_VALIDATION = "requires_validation"
    AWAITING_VALIDATION = "awaiting_validation"
    AUTHENTICATED = "authenticated"
    BAD_PASSWORD = "bad_password"
    INVALID_VERIFICATION_CODE = "invalid_verification_code"


class Authenticator:
    def __init__(self, api, login_method, username, password,
                 access_token_cache_file=None):
        self._api = api
        self._login_method = login_method
        self._username = username
        self._password = password
        self._access_token_cache_file = access_token_cache_file

        if (access_token_cache_file is not None and
                os.path.exists(access_token_cache_file)):
            with open(access_token_cache_file, 'r') as f:
                self._authentication = from_authentication_json(json.load(f))
        else:
            self._authentication = Authentication(AuthenticationState.NONE)

    def _update_authentication_state(self, state):
        self._authentication.state = state
        self._cache()

    def _cache(self):
        if self._access_token_cache_file is not None:
            with open(self._access_token_cache_file, "w") as f:
                f.write(to_authentication_json(self._authentication))

    def authenticate(self, verification_code=None):
        state = self._authentication.state

        if state in [AuthenticationState.NONE,
                     AuthenticationState.BAD_PASSWORD]:
            self._get_session()
        elif state in [AuthenticationState.REQUIRES_VALIDATION,
                       AuthenticationState.INVALID_VERIFICATION_CODE]:
            self._send_verification_code()
        elif AuthenticationState.AWAITING_VALIDATION == state:
            self._validate_verification_code(verification_code)

        return self._authentication

    def _get_session(self):
        identifier = self._login_method + ":" + self._username
        install_id = self._authentication.install_id
        response = self._api.get_session(install_id, identifier,
                                         self._password)

        data = response.json()
        access_token = response.headers[HEADER_AUGUST_ACCESS_TOKEN]
        access_token_expires = data["expiresAt"]
        v_password = data["vPassword"]
        v_install_id = data["vInstallId"]
        state = AuthenticationState.NONE

        if v_password == False:
            state = AuthenticationState.BAD_PASSWORD
        elif v_install_id == False:
            state = AuthenticationState.REQUIRES_VALIDATION
        else:
            state = AuthenticationState.AUTHENTICATED

        self._authentication = Authentication(state, install_id, access_token,
                                              access_token_expires)
        self._cache()

    def _send_verification_code(self):
        response = self._api.send_verification_code(
            self._authentication.access_token, self._login_method,
            self._username)
        self._update_authentication_state(
            AuthenticationState.AWAITING_VALIDATION)

    def _validate_verification_code(self, verification_code):
        if not verification_code:
            self._update_authentication_state(
                AuthenticationState.INVALID_VERIFICATION_CODE)

        try:
            response = self._api.validate_verification_code(
                self._authentication.access_token, self._login_method,
                self._username, verification_code)
            self._get_session()
        except requests.exceptions.RequestException:
            self._update_authentication_state(
                AuthenticationState.INVALID_VERIFICATION_CODE)
