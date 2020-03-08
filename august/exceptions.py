from requests.exceptions import HTTPError


class AugustApiAIOHTTPError(Exception):
    """An august api error with a friendly user consumable string."""


class AugustApiHTTPError(HTTPError):
    """An august api error with a friendly user consumable string."""
