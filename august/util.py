import datetime

from august.activity import (
    ACTIVITY_ACTION_STATES,
    DoorOperationActivity,
    LockOperationActivity,
)


def update_lock_detail_from_activity(lock_detail, activity):
    """Update the LockDetail from an activity."""
    activity_end_time_utc = as_utc_from_local(activity.activity_end_time)
    if activity.house_id != lock_detail.house_id:
        raise ValueError
    if activity.device_id != lock_detail.device_id:
        raise ValueError
    if isinstance(activity, LockOperationActivity):
        if lock_detail.lock_status_datetime >= activity_end_time_utc:
            return False
        lock_detail.lock_status = ACTIVITY_ACTION_STATES[activity.action]
        lock_detail.lock_status_datetime = activity_end_time_utc
    elif isinstance(activity, DoorOperationActivity):
        if lock_detail.door_state_datetime >= activity_end_time_utc:
            return False
        lock_detail.door_state = ACTIVITY_ACTION_STATES[activity.action]
        lock_detail.door_state_datetime = activity_end_time_utc
    else:
        raise ValueError

    return True


def as_utc_from_local(dtime):
    """Converts the datetime returned from an activity to UTC."""
    return dtime.astimezone(tz=datetime.timezone.utc)
