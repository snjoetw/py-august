class Device:
    def __init__(self, device_id, device_name, house_id):
        self._device_id = device_id
        self._device_name = device_name
        self._house_id = house_id

    @property
    def device_id(self):
        return self._device_id

    @property
    def device_name(self):
        return self._device_name

    @property
    def house_id(self):
        return self._house_id


class DeviceDetail:
    def __init__(
        self,
        device_id,
        device_name,
        house_id,
        serial_number,
        firmware_version,
        pubsub_channel,
    ):
        self._device_id = device_id
        self._device_name = device_name
        self._house_id = house_id
        self._serial_number = serial_number
        self._firmware_version = firmware_version
        self._pubsub_channel = pubsub_channel

    @property
    def device_id(self):
        return self._device_id

    @property
    def device_name(self):
        return self._device_name

    @property
    def house_id(self):
        return self._house_id

    @property
    def serial_number(self):
        return self._serial_number

    @property
    def firmware_version(self):
        return self._firmware_version

    @property
    def pubsub_channel(self):
        return self._pubsub_channel
