"""Connect to pubnub."""

import datetime
import logging

from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub_asyncio import PubNubAsyncio

AUGUST_CHANNEL = "sub-c-1030e062-0ebe-11e5-a5c2-0619f8945a4f"

_LOGGER = logging.getLogger(__name__)


class AugustPubNub(SubscribeCallback):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connected = False
        self._device_channels = {}
        self._subscriptions = []

    def presence(self, pubnub, presence):
        pass  # handle incoming presence data

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            self.connected = False

        elif status.category in (
            PNStatusCategory.PNReconnectedCategory,
            PNStatusCategory.PNConnectedCategory,
        ):
            self.connected = True

    def message(self, pubnub, message):
        # Handle new messages
        device_id = self._device_channels[message.channel]
        _LOGGER.debug(
            "Recieved new messages on channel %s for device_id: %s with timetoken: %s: %s",
            message.channel,
            device_id,
            message.timetoken,
            message.message,
        )
        for callback in self._subscriptions:
            callback(
                device_id,
                datetime.datetime.fromtimestamp(
                    int(message.timetoken) / 10000000, tz=datetime.timezone.utc
                ),
                message.message,
            )

    def subscribe(self, update_callback):
        """Add an callback subscriber.

        Returns a callable that can be used to unsubscribe.
        """
        self._subscriptions.append(update_callback)

        def _unsubscribe():
            self._subscriptions.remove(update_callback)

        return _unsubscribe

    def register_device(self, device_detail):
        """Regiter a device to get updates."""
        if device_detail.pubsub_channel is None:
            return
        self._device_channels[device_detail.pubsub_channel] = device_detail.device_id

    @property
    def channels(self):
        """Return a list of registered channels."""
        return self._device_channels.keys()


def async_create_pubnub(user_uuid, subscriptions):
    """Create a pubnub subscription."""
    pnconfig = PNConfiguration()
    pnconfig.subscribe_key = AUGUST_CHANNEL
    pnconfig.uuid = f"pn-{str(user_uuid).upper()}"
    pubnub = PubNubAsyncio(pnconfig)
    pubnub.add_listener(subscriptions)
    pubnub.subscribe().channels(subscriptions.channels).execute()

    def _unsub():
        pubnub.unsubscribe().channels(subscriptions.channels).execute()

    return _unsub
