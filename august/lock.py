from enum import Enum

from august.device import Device


class Lock(Device):
    def __init__(self, device_id, data):
        super().__init__(
            device_id,
            data["LockName"],
            data["HouseID"],
        )

    def __repr__(self):
        return "Lock(id={}, name={}, house_id={})".format(
            self.device_id,
            self.device_name,
            self.house_id)


class LockStatus(Enum):
    LOCKED = "kAugLockState_Locked"
    UNLOCKED = "kAugLockState_Unlocked"
