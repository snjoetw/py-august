import json
import unittest
import os

from august.activity import (
    ACTION_DOOR_CLOSED,
    ACTION_DOOR_OPEN,
    ACTION_DOORBELL_CALL_HANGUP,
    ACTION_DOORBELL_CALL_INITIATED,
    ACTION_DOORBELL_CALL_MISSED,
    ACTION_DOORBELL_MOTION_DETECTED,
    ACTION_LOCK_LOCK,
    ACTION_LOCK_ONETOUCHLOCK,
    ACTION_LOCK_UNLOCK,
    ACTIVITY_ACTION_STATES,
    ACTIVITY_ACTIONS_DOOR_OPERATION,
    ACTIVITY_ACTIONS_DOORBELL_DING,
    ACTIVITY_ACTIONS_DOORBELL_MOTION,
    ACTIVITY_ACTIONS_DOORBELL_VIEW,
    ACTIVITY_ACTIONS_LOCK_OPERATION,
    LockOperationActivity,
)
from august.lock import LockDoorStatus, LockStatus


def load_fixture(filename):
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path) as fptr:
        return fptr.read()


class TestActivity(unittest.TestCase):
    def test_activity_action_states(self):
        self.assertIs(
            ACTIVITY_ACTION_STATES[ACTION_LOCK_ONETOUCHLOCK], LockStatus.LOCKED
        )
        self.assertIs(ACTIVITY_ACTION_STATES[ACTION_LOCK_LOCK], LockStatus.LOCKED)
        self.assertIs(ACTIVITY_ACTION_STATES[ACTION_LOCK_UNLOCK], LockStatus.UNLOCKED)
        self.assertIs(ACTIVITY_ACTION_STATES[ACTION_DOOR_CLOSED], LockDoorStatus.CLOSED)
        self.assertIs(ACTIVITY_ACTION_STATES[ACTION_DOOR_OPEN], LockDoorStatus.OPEN)

    def test_activity_actions(self):
        self.assertCountEqual(
            ACTIVITY_ACTIONS_DOORBELL_DING,
            [ACTION_DOORBELL_CALL_MISSED, ACTION_DOORBELL_CALL_HANGUP],
        )
        self.assertCountEqual(
            ACTIVITY_ACTIONS_DOORBELL_MOTION, [ACTION_DOORBELL_MOTION_DETECTED]
        )
        self.assertCountEqual(
            ACTIVITY_ACTIONS_DOORBELL_VIEW, [ACTION_DOORBELL_CALL_INITIATED]
        )
        self.assertCountEqual(
            ACTIVITY_ACTIONS_LOCK_OPERATION,
            [ACTION_LOCK_ONETOUCHLOCK, ACTION_LOCK_LOCK, ACTION_LOCK_UNLOCK],
        )
        self.assertCountEqual(
            ACTIVITY_ACTIONS_DOOR_OPERATION, [ACTION_DOOR_OPEN, ACTION_DOOR_CLOSED]
        )

    def test_auto_unlock_activity(self):
        auto_unlock_activity = LockOperationActivity(
            json.loads(load_fixture("auto_unlock_activity.json"))
        )
        assert auto_unlock_activity.operated_by == "My Name"
        assert auto_unlock_activity.operated_remote is False
        assert auto_unlock_activity.operated_keypad is False

    def test_bluetooth_lock_activity(self):
        bluetooth_lock_activity = LockOperationActivity(
            json.loads(load_fixture("bluetooth_lock_activity.json"))
        )
        assert bluetooth_lock_activity.operated_by == "I have a picture"
        assert bluetooth_lock_activity.operated_remote is False
        assert bluetooth_lock_activity.operated_keypad is False
        assert bluetooth_lock_activity.operator_image_url == "https://image.url"
        assert bluetooth_lock_activity.operator_thumbnail_url == "https://thumbnail.url"

    def test_keypad_lock_activity(self):
        keypad_lock_activity = LockOperationActivity(
            json.loads(load_fixture("keypad_lock_activity.json"))
        )
        assert keypad_lock_activity.operated_by == "My Name"
        assert keypad_lock_activity.operated_remote is False
        assert keypad_lock_activity.operated_keypad is True

    def test_remote_lock_activity(self):
        remote_lock_activity = LockOperationActivity(
            json.loads(load_fixture("remote_lock_activity.json"))
        )
        assert remote_lock_activity.operated_by == "My Name"
        assert remote_lock_activity.operated_remote is True
        assert remote_lock_activity.operated_keypad is False

    def test_lock_activity(self):
        lock_operation_activity = LockOperationActivity(
            json.loads(load_fixture("lock_activity.json"))
        )
        assert lock_operation_activity.operated_by == "MockHouse House"
        assert lock_operation_activity.operated_remote is True
        assert lock_operation_activity.operated_keypad is False
        assert lock_operation_activity.operated_autorelock is False

    def test_unlock_activity(self):
        unlock_operation_activity = LockOperationActivity(
            json.loads(load_fixture("unlock_activity.json"))
        )
        assert unlock_operation_activity.operated_by == "MockHouse House"
        assert unlock_operation_activity.operated_keypad is False
        assert unlock_operation_activity.operated_remote is True
        assert unlock_operation_activity.operator_image_url is None
        assert unlock_operation_activity.operated_autorelock is False
        assert unlock_operation_activity.operator_thumbnail_url is None

    def test_autorelock_activity(self):
        auto_relock_operation_activity = LockOperationActivity(
            json.loads(load_fixture("auto_relock_activity.json"))
        )
        assert auto_relock_operation_activity.operated_by == "I have no picture"
        assert auto_relock_operation_activity.operated_remote is False
        assert auto_relock_operation_activity.operated_autorelock is True
        assert auto_relock_operation_activity.operated_keypad is False
