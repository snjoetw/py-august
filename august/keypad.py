from august.device import DeviceDetail


class KeypadDetail(DeviceDetail):
    def __init__(self, house_id, data):
        super().__init__(
            data["_id"],
            None,
            house_id,
            data["serialNumber"],
            data["currentFirmwareVersion"]
        )

        self._battery_level = data["batteryLevel"]

    @property
    def battery_level(self):
        return self._battery_level
