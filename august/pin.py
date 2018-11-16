import dateutil.parser

class Pin(object):
    def __init__(self, _id, lockID, userID, state, pin, slot,
                 accessType, createdAt, updatedAt, loadedDate,
                 firstName, lastName, unverified, accessStartTime=None,
                 accessEndTime=None, accessTimes=None):
        self.id = _id
        self.lockID = lockID
        self.userID = userID
        self.state = state
        self.pin = pin
        self.slot = slot
        self.accessType = accessType
        self.firstName = firstName
        self.lastName = lastName
        self.unverified = unverified

        self._createdAt = createdAt
        self._updatedAt = updatedAt
        self._loadedDate = loadedDate
        self._accessStartTime = accessStartTime
        self._accessEndTime = accessEndTime
        self._accessTimes = accessTimes

    @property
    def createdAt(self):
        return dateutil.parser.parse(self._createdAt)

    @property
    def updatedAt(self):
        return dateutil.parser.parse(self._updatedAt)

    @property
    def loadedDate(self):
        return dateutil.parser.parse(self._loadedDate)

    @property
    def accessStartTime(self):
        if not self._accessStartTime:
            return None
        return dateutil.parser.parse(self._accessStartTime)

    @property
    def accessEndTime(self):
        if not self._accessEndTime:
            return None
        return dateutil.parser.parse(self._accessEndTime)

    @property
    def accessTimes(self):
        if not self._accessTimes:
            return None
        return dateutil.parser.parse(self._accessTimes)

    def __repr__(self):
        return "Pin(id={} firstName={}, lastName={})".format(
            self.id,
            self.firstName,
            self.lastName
        )
