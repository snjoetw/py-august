import vol as vol

ACTIVITY_FETCH_LIMIT = 10


class August:
    def __init__(self, api, access_token):
        self._api = api
        self._access_token = access_token

        self._doorbells = self._api.get_doorbells(self._access_token)
        self._locks = self._api.get_locks(self._access_token)
        self._activities = vol.collections.defaultdict(dict)

        for device in self._doorbells + self._locks:
            house_id = device.house_id
            device_id = device.device_id
            self._activities[house_id][device_id] = []

        self.update_house_activities()

    def update_house_activities(self, limit=ACTIVITY_FETCH_LIMIT):
        for house_id in self._activities.keys():
            activities = self._api.get_house_activities(self._access_token,
                                                        house_id,
                                                        limit=limit)
            for activity in activities:
                device_id = activity.device_id
                self._activities[house_id][device_id] = activities

    def update_lock_status(self):
        for lock in self._locks:
            self._api.get_lock_status(self._access_token,
                                      lock.device_id)

    def get_activities(self, house_id, device_id, *activity_types):
        """Return a list of activities."""
        activities = self._activities.get(house_id, {}).get(device_id, [])

        if activity_types:
            return [a for a in activities if a.activity_type in activity_types]

        return activities

    def lock(self, device_id):
        return self._api.lock(self._access_token, device_id)

    def unlock(self, device_id):
        return self._api.unlock(self._access_token, device_id)

    @property
    def doorbells(self):
        """Return a list of doorbells."""
        return self._doorbells

    @property
    def locks(self):
        """Return a list of locks."""
        return self._locks
