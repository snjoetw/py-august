class Doorbell:
    def __init__(self, data):
        self._id = data["doorbellID"]
        self._serial_number = data["serialNumber"]
        self._name = data["name"]
        self._status = data["status"]
        self._house_id = data["HouseID"]
        recent_image = data.get("recentImage", {})
        self._image_url = recent_image.get("secure_url", None)
        self._has_subscription = data.get("dvrSubscriptionSetupDone", False)

    @property
    def device_id(self):
        return self._id

    @property
    def serial_number(self):
        return self._serial_number

    @property
    def name(self):
        return self._name

    @property
    def status(self):
        return self._status

    @property
    def house_id(self):
        return self._house_id

    @property
    def image_url(self):
        return self._image_url

    @property
    def has_subscription(self):
        return self._has_subscription

    def __repr__(self):
        return "Doorbell(id={}, name={}, house_id={})".format(
            self._id,
            self._name,
            self._house_id)
