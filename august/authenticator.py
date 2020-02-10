import base64
import json
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum

import dateutil.parser
import requests

from august.api import HEADER_AUGUST_ACCESS_TOKEN

# The default time before expiration to refresh a token
DEFAULT_RENEWAL_THRESHOLD = timedelta(days=7)

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

    def parsed_expiration_time(self):
        return dateutil.parser.parse(self.access_token_expires)

    def is_expired(self):
        return self.parsed_expiration_time() < datetime.now(timezone.utc)


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
                 access_token_cache_file=None,
                 access_token_renewal_threshold=DEFAULT_RENEWAL_THRESHOLD):
        self._api = api
        self._login_method = login_method
        self._username = username
        self._password = password
        self._access_token_cache_file = access_token_cache_file
        self._access_token_renewal_threshold = access_token_renewal_threshold

        if (access_token_cache_file is not None and
                os.path.exists(access_token_cache_file)):
            with open(access_token_cache_file, 'r') as file:
                try:
                    self._authentication = from_authentication_json(
                        json.load(file))

                    # If token is to expire within 7 days then print a warning.
                    if self._authentication.is_expired():
                        _LOGGER.error("Token has expired.")
                        self._authentication = Authentication(
                            AuthenticationState.REQUIRES_AUTHENTICATION,
                            install_id=install_id)
                    # If token is not expired but less then 7 days before it
                    # will.
                    elif (self._authentication.parsed_expiration_time()
                          - datetime.now(timezone.utc)) < timedelta(days=7):
                        exp_time = self._authentication.access_token_expires
                        _LOGGER.warning("API Token is going to expire at %s "
                                        "hours. Deleting file %s will result "
                                        "in a new token being requested next"
                                        " time",
                                        exp_time,
                                        access_token_cache_file)
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

    def should_refresh(self):
        return (self._authentication.state ==
                AuthenticationState.AUTHENTICATED and (
                    (self._authentication.parsed_expiration_time()
                     - datetime.now(timezone.utc))
                    < self._access_token_renewal_threshold))

    def refresh_access_token(self, force=False):
        if not self.should_refresh() and not force:
            return self._authentication

        if self._authentication.state != AuthenticationState.AUTHENTICATED:
            _LOGGER.warning(
                "Tried to refresh access token when not authenticated")
            return self._authentication

        refreshed_token = self._api.refresh_access_token(
            self._authentication.access_token)
        jwt_parts = refreshed_token.split(".")
        jwt_claims = json.loads(base64.b64decode(jwt_parts[1] + '==='))

        if 'exp' not in jwt_claims:
            _LOGGER.warning("Did not find expected `exp' claim in JWT")
            return self._authentication

        new_expiration = datetime.utcfromtimestamp(jwt_claims['exp'])
        # The august api always returns expiresAt in the format
        # '%Y-%m-%dT%H:%M:%S.%fZ'
        # from the get_session api call
        # It is important we store access_token_expires formatted
        # the same way for compatbility
        self._authentication = Authentication(
            self._authentication.state,
            install_id=self._authentication.install_id,
            access_token=refreshed_token,
            access_token_expires=new_expiration.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
        self._cache_authentication(self._authentication)

        _LOGGER.info("Successfully refreshed access token")
        return self._authentication

    def _cache_authentication(self, authentication):
        if self._access_token_cache_file is not None:
            with open(self._access_token_cache_file, "w") as file:
                file.write(to_authentication_json(authentication))
