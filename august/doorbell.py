from august.device import Device, DeviceDetail


class Doorbell(Device):
    def __init__(self, device_id, data):
        super().__init__(device_id, data["name"], data["HouseID"])
        self._serial_number = data["serialNumber"]
        self._status = data["status"]
        recent_image = data.get("recentImage", {})
        self._image_url = recent_image.get("secure_url", None)
        self._has_subscription = data.get("dvrSubscriptionSetupDone", False)

    @property
    def serial_number(self):
        return self._serial_number

    @property
    def status(self):
        return self._status

    @property
    def is_online(self):
        return self.status == 'doorbell_call_status_online'

    @property
    def image_url(self):
        return self._image_url

    @property
    def has_subscription(self):
        return self._has_subscription

    def __repr__(self):
        return "Doorbell(id={}, name={}, house_id={})".format(
            self.device_id,
            self.device_name,
            self.house_id)


class DoorbellDetail(DeviceDetail):
    def __init__(self, data):
        super().__init__(
            data["doorbellID"],
            data["name"],
            data["HouseID"],
            data["serialNumber"],
            data["firmwareVersion"])

        self._status = data["status"]
        recent_image = data.get("recentImage", {})
        self._image_url = recent_image.get("secure_url", None)
        self._has_subscription = data.get("dvrSubscriptionSetupDone", False)

    @property
    def status(self):
        return self._status

    @property
    def is_online(self):
        return self.status == 'doorbell_call_status_online'

    @property
    def image_url(self):
        return self._image_url

    @property
    def has_subscription(self):
        return self._has_subscription
