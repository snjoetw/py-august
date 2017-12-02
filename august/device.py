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
