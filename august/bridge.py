from enum import Enum

from august.device import DeviceDetail

ONLINE_EVENT = "associated_bridge_online"
OFFLINE_EVENT = "associated_bridge_offline"


class BridgeStatus(Enum):
    OFFLINE = "offline"
    ONLINE = "online"
    UNKNOWN = "unknown"


class BridgeDetail(DeviceDetail):
    def __init__(self, house_id, data):
        super().__init__(
            data["_id"], None, house_id, None, data["firmwareVersion"], None
        )

        self._operative = data["operative"]

        if "status" in data:
            self._status = BridgeStatusDetail(data["status"])
        else:
            self._status = None

    @property
    def status(self):
        return self._status

    @property
    def operative(self):
        return self._operative

    def set_online(self, state):
        """Called when the bridge online state changes."""
        self._status.set_online(state)


class BridgeStatusDetail:
    def __init__(self, data):
        self._current = BridgeStatus.UNKNOWN

        if "current" in data and data["current"] == "online":
            self._current = BridgeStatus.ONLINE

        self._updated = data["updated"] if "updated" in data else None
        self._last_online = data["lastOnline"] if "lastOnline" in data else None
        self._last_offline = data["lastOffline"] if "lastOffline" in data else None

    @property
    def current(self):
        return self._current

    def set_online(self, state):
        """Called when the bridge online state changes."""
        self._current = BridgeStatus.ONLINE if state else BridgeStatus.OFFLINE

    @property
    def updated(self):
        return self._updated

    @property
    def last_online(self):
        return self._last_online

    @property
    def last_offline(self):
        return self._last_offline
