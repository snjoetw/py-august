from requests.exceptions import HTTPError


class AugustApiHTTPError(HTTPError):
    """An august api error with a friendly user consumable string."""
