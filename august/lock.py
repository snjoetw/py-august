from enum import Enum

from august.bridge import BridgeDetail
from august.device import Device, DeviceDetail
from august.keypad import KeypadDetail


class Lock(Device):
    def __init__(self, device_id, data):
        super().__init__(
            device_id, data["LockName"], data["HouseID"],
        )
        self._user_type = data["UserType"]

    @property
    def is_operable(self):
        return self._user_type == "superuser"

    def __repr__(self):
        return "Lock(id={}, name={}, house_id={})".format(
            self.device_id, self.device_name, self.house_id
        )


class LockDetail(DeviceDetail):
    def __init__(self, data):
        super().__init__(
            data["LockID"],
            data["LockName"],
            data["HouseID"],
            data["SerialNumber"],
            data["currentFirmwareVersion"],
        )

        if "Bridge" in data:
            self._bridge = BridgeDetail(self.house_id, data["Bridge"])
        else:
            self._bridge = None

        self._doorsense = False
        if "LockStatus" in data:
            if "doorState" in data["LockStatus"]:
                self._doorsense = True

        if "keypad" in data:
            self._keypad_detail = KeypadDetail(self.house_id, data["keypad"])
        else:
            self._keypad_detail = None

        self._battery_level = int(100 * data["battery"])

    @property
    def battery_level(self):
        return self._battery_level

    @property
    def keypad(self):
        return self._keypad_detail

    @property
    def bridge(self):
        return self._bridge

    @property
    def doorsense(self):
        return self._doorsense


class LockStatus(Enum):
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    UNKNOWN = "unknown"


class LockDoorStatus(Enum):
    CLOSED = "closed"
    OPEN = "open"
    UNKNOWN = "unknown"
