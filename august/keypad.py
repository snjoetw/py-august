from august.device import DeviceDetail

BATTERY_LEVEL_FULL = "Full"
BATTERY_LEVEL_MEDIUM = "Medium"
BATTERY_LEVEL_LOW = "Low"


class KeypadDetail(DeviceDetail):
    def __init__(self, house_id, keypad_name, data):
        super().__init__(
            data["_id"],
            keypad_name,
            house_id,
            data["serialNumber"],
            data["currentFirmwareVersion"],
        )

        self._battery_level = data["batteryLevel"]

    @property
    def model(self):
        return "AK-R1"

    @property
    def battery_level(self):
        return self._battery_level

    @property
    def battery_percentage(self):
        """Return an approximation of the battery percentage."""
        if not self._battery_level:
            return None

        if self._battery_level == BATTERY_LEVEL_FULL:
            return 100
        if self._battery_level == BATTERY_LEVEL_MEDIUM:
            return 60
        if self._battery_level == BATTERY_LEVEL_LOW:
            return 10

        return 0
