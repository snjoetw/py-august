from august.device import DeviceDetail


class KeypadDetail(DeviceDetail):
    def __init__(self, house_id, keypad_name, data):
        super().__init__(
            data["_id"],
            keypad_name,
            house_id,
            data["serialNumber"],
            data["currentFirmwareVersion"]
        )

        self._battery_level = data["batteryLevel"]

    @property
    def model(self):
        return "AK-R1"

    @property
    def battery_level(self):
        return self._battery_level
