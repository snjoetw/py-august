import dateutil.parser


class Pin:
    def __init__(self, data):
        self._pin_id = data["_id"]
        self._lock_id = data["lockID"]
        self._user_id = data["userID"]
        self._state = data["state"]
        self._pin = data["pin"]
        self._slot = data["slot"]
        self._access_type = data["accessType"]
        self._first_name = data["firstName"]
        self._last_name = data["lastName"]
        self._unverified = data["unverified"]

        self._created_at = data["createdAt"]
        self._updated_at = data["updatedAt"]
        self._loaded_date = data["loadedDate"]
        self._access_start_time = data["accessStartTime"]
        self._access_end_time = data["accessEndTime"]
        self._access_times = data["accessTimes"]

    @property
    def pin_id(self):
        return self._pin_id

    @property
    def lock_id(self):
        return self._lock_id

    @property
    def user_id(self):
        return self._user_id

    @property
    def state(self):
        return self._state

    @property
    def pin(self):
        return self._pin

    @property
    def slot(self):
        return self._slot

    @property
    def access_type(self):
        return self._access_type

    @property
    def first_name(self):
        return self._first_name

    @property
    def last_name(self):
        return self._last_name

    @property
    def unverified(self):
        return self._unverified

    @property
    def created_at(self):
        return dateutil.parser.parse(self._created_at)

    @property
    def updated_at(self):
        return dateutil.parser.parse(self._updated_at)

    @property
    def loaded_date(self):
        return dateutil.parser.parse(self._loaded_date)

    @property
    def access_start_time(self):
        if not self._access_start_time:
            return None
        return dateutil.parser.parse(self._access_start_time)

    @property
    def access_end_time(self):
        if not self._access_end_time:
            return None
        return dateutil.parser.parse(self._access_end_time)

    @property
    def access_times(self):
        if not self._access_times:
            return None
        return dateutil.parser.parse(self._access_times)

    def __repr__(self):
        return "Pin(id={} firstName={}, lastName={})".format(
            self.pin_id,
            self.first_name,
            self.last_name
        )
