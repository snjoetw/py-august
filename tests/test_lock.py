import json
import os
import unittest

import dateutil.parser
import datetime

from august.activity import DoorOperationActivity, LockOperationActivity
from august.lock import LockDetail, LockDoorStatus, LockStatus
from august.util import update_lock_detail_from_activity, as_utc_from_local


def load_fixture(filename):
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path) as fptr:
        return fptr.read()


class TestLockDetail(unittest.TestCase):
    def test_update_lock_with_activity(self):
        lock = LockDetail(
            json.loads(load_fixture("get_lock.online_with_doorsense.json"))
        )
        self.assertEqual("ABC", lock.device_id)
        self.assertEqual(LockStatus.LOCKED, lock.lock_status)
        self.assertEqual(LockDoorStatus.OPEN, lock.door_state)
        self.assertEqual(
            dateutil.parser.parse("2017-12-10T04:48:30.272Z"), lock.lock_status_datetime
        )
        self.assertEqual(
            dateutil.parser.parse("2017-12-10T04:48:30.272Z"), lock.door_state_datetime
        )

        lock_operation_activity = LockOperationActivity(
            json.loads(load_fixture("lock_activity.json"))
        )
        unlock_operation_activity = LockOperationActivity(
            json.loads(load_fixture("unlock_activity.json"))
        )
        open_operation_activity = DoorOperationActivity(
            json.loads(load_fixture("door_open_activity.json"))
        )
        closed_operation_activity = DoorOperationActivity(
            json.loads(load_fixture("door_closed_activity.json"))
        )
        closed_operation_wrong_deviceid_activity = DoorOperationActivity(
            json.loads(load_fixture("door_closed_activity_wrong_deviceid.json"))
        )
        closed_operation_wrong_houseid_activity = DoorOperationActivity(
            json.loads(load_fixture("door_closed_activity_wrong_houseid.json"))
        )

        self.assertTrue(
            update_lock_detail_from_activity(lock, unlock_operation_activity)
        )
        self.assertEqual(LockStatus.UNLOCKED, lock.lock_status)
        self.assertEqual(
            as_utc_from_local(datetime.datetime.fromtimestamp(1582007217000 / 1000)),
            lock.lock_status_datetime,
        )

        self.assertTrue(update_lock_detail_from_activity(lock, lock_operation_activity))
        self.assertEqual(LockStatus.LOCKED, lock.lock_status)
        self.assertEqual(
            as_utc_from_local(datetime.datetime.fromtimestamp(1582007218000 / 1000)),
            lock.lock_status_datetime,
        )

        # returns false we send an older activity
        self.assertFalse(
            update_lock_detail_from_activity(lock, unlock_operation_activity)
        )

        self.assertTrue(
            update_lock_detail_from_activity(lock, closed_operation_activity)
        )
        self.assertEqual(LockDoorStatus.CLOSED, lock.door_state)
        self.assertEqual(
            as_utc_from_local(datetime.datetime.fromtimestamp(1582007217000 / 1000)),
            lock.door_state_datetime,
        )

        self.assertTrue(update_lock_detail_from_activity(lock, open_operation_activity))
        self.assertEqual(LockDoorStatus.OPEN, lock.door_state)
        self.assertEqual(
            as_utc_from_local(datetime.datetime.fromtimestamp(1582007219000 / 1000)),
            lock.door_state_datetime,
        )

        # returns false we send an older activity
        self.assertFalse(
            update_lock_detail_from_activity(lock, closed_operation_activity)
        )

        with self.assertRaises(ValueError):
            update_lock_detail_from_activity(
                lock, closed_operation_wrong_deviceid_activity
            )

        with self.assertRaises(ValueError):
            update_lock_detail_from_activity(
                lock, closed_operation_wrong_houseid_activity
            )
