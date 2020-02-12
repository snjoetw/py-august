import os
import unittest

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
)
from august.lock import LockDoorStatus, LockStatus


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
