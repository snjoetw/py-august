from datetime import datetime
from enum import Enum

from august.lock import LockDoorStatus, LockStatus

ACTION_LOCK_ONETOUCHLOCK = "onetouchlock"
ACTION_LOCK_LOCK = "lock"
ACTION_LOCK_UNLOCK = "unlock"
ACTION_DOOR_OPEN = "dooropen"
ACTION_DOOR_CLOSED = "doorclosed"
ACTION_DOORBELL_CALL_INITIATED = "doorbell_call_initiated"
ACTION_DOORBELL_MOTION_DETECTED = "doorbell_motion_detected"
ACTION_DOORBELL_CALL_MISSED = "doorbell_call_missed"
ACTION_DOORBELL_CALL_HANGUP = "doorbell_call_hangup"

ACTIVITY_ACTIONS_DOORBELL_DING = [ACTION_DOORBELL_CALL_MISSED, ACTION_DOORBELL_CALL_HANGUP]
ACTIVITY_ACTIONS_DOORBELL_MOTION = [ACTION_DOORBELL_MOTION_DETECTED]
ACTIVITY_ACTIONS_DOORBELL_VIEW = [ACTION_DOORBELL_CALL_INITIATED]
ACTIVITY_ACTIONS_LOCK_OPERATION = [ACTION_LOCK_LOCK, ACTION_LOCK_UNLOCK, ACTION_LOCK_ONETOUCHLOCK]
ACTIVITY_ACTIONS_DOOR_OPERATION = [ACTION_DOOR_CLOSED, ACTION_DOOR_OPEN]

ACTIVITY_ACTION_STATES = {
    ACTION_LOCK_ONETOUCHLOCK: LockStatus.LOCKED,
    ACTION_LOCK_LOCK: LockStatus.LOCKED,
    ACTION_LOCK_UNLOCK: LockStatus.UNLOCKED,
    ACTION_DOOR_OPEN: LockDoorStatus.OPEN,
    ACTION_DOOR_CLOSED: LockDoorStatus.CLOSED,
}


def epoch_to_datetime(epoch):
    return datetime.fromtimestamp(int(epoch) / 1000.0)


class ActivityType(Enum):
    DOORBELL_MOTION = "doorbell_motion"
    DOORBELL_DING = "doorbell_ding"
    DOORBELL_VIEW = "doorbell_view"
    LOCK_OPERATION = "lock_operation"
    DOOR_OPERATION = "door_operation"


class Activity:
    def __init__(self, activity_type, data):
        self._activity_type = activity_type

        entities = data.get("entities", {})
        self._activity_id = entities.get("activity")
        self._house_id = entities.get("house")

        self._activity_time = epoch_to_datetime(data.get("dateTime"))
        self._action = data.get("action")
        self._device_id = data.get("deviceID")
        self._device_name = data.get("deviceName")
        self._device_type = data.get("deviceType")

    @property
    def activity_type(self):
        return self._activity_type

    @property
    def activity_id(self):
        return self._activity_id

    @property
    def house_id(self):
        return self._house_id

    @property
    def activity_start_time(self):
        return self._activity_time

    @property
    def activity_end_time(self):
        return self._activity_time

    @property
    def action(self):
        return self._action

    @property
    def device_id(self):
        return self._device_id

    @property
    def device_name(self):
        return self._device_name

    @property
    def device_type(self):
        return self._device_type


class DoorbellMotionActivity(Activity):
    def __init__(self, data):
        super().__init__(ActivityType.DOORBELL_MOTION, data)

        image = data.get("info", {}).get("image")
        self._image_url = None if image is None else image.get("secure_url")

    @property
    def image_url(self):
        return self._image_url


class DoorbellDingActivity(Activity):
    def __init__(self, data):
        super().__init__(ActivityType.DOORBELL_DING, data)

        info = data.get("info", {})
        self._activity_start_time = epoch_to_datetime(info.get("started"))
        self._activity_end_time = epoch_to_datetime(info.get("ended"))
        self._image_url = info.get("image")

    @property
    def image_url(self):
        return self._image_url

    @property
    def activity_start_time(self):
        return self._activity_start_time

    @property
    def activity_end_time(self):
        return self._activity_end_time


class DoorbellViewActivity(Activity):
    def __init__(self, data):
        super().__init__(ActivityType.DOORBELL_VIEW, data)

        info = data.get("info", {})
        self._activity_start_time = epoch_to_datetime(info.get("started"))
        self._activity_end_time = epoch_to_datetime(info.get("ended"))
        self._image_url = info.get("image")

    @property
    def image_url(self):
        return self._image_url

    @property
    def activity_start_time(self):
        return self._activity_start_time

    @property
    def activity_end_time(self):
        return self._activity_end_time


class LockOperationActivity(Activity):
    def __init__(self, data):
        super().__init__(ActivityType.LOCK_OPERATION, data)

        calling_user = data.get("callingUser", {})
        self._operated_by = "{} {}".format(
            calling_user.get("FirstName"),
            calling_user.get("LastName"),
        )

    @property
    def operated_by(self):
        return self._operated_by


class DoorOperationActivity(Activity):
    def __init__(self, data):
        super().__init__(ActivityType.DOOR_OPERATION, data)
