import json
import os
import unittest

import dateutil.parser
import datetime

from august.activity import (
    DoorOperationActivity,
    LockOperationActivity,
    DoorbellMotionActivity,
)
from august.lock import LockDetail, LockDoorStatus, LockStatus
from august.doorbell import DoorbellDetail
from august.util import (
    update_lock_detail_from_activity,
    as_utc_from_local,
    update_doorbell_image_from_activity,
)
from august.api import _convert_lock_result_to_activities


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

        # We do not always have the houseid so we do not throw
        # as long as the deviceid is correct since they are unique
        self.assertFalse(
            update_lock_detail_from_activity(
                lock, closed_operation_wrong_houseid_activity
            )
        )

        self.assertEqual(LockDoorStatus.OPEN, lock.door_state)
        self.assertEqual(LockStatus.LOCKED, lock.lock_status)
        activities = _convert_lock_result_to_activities(
            json.loads(load_fixture("unlock.json"))
        )
        for activity in activities:
            self.assertTrue(update_lock_detail_from_activity(lock, activity))
        self.assertEqual(LockDoorStatus.CLOSED, lock.door_state)
        self.assertEqual(LockStatus.UNLOCKED, lock.lock_status)


class TestDetail(unittest.TestCase):
    def test_update_doorbell_image_from_activity(self):
        doorbell = DoorbellDetail(json.loads(load_fixture("get_doorbell.json")))
        self.assertEqual("K98GiDT45GUL", doorbell.device_id)
        self.assertEqual(
            dateutil.parser.parse("2017-12-10T08:01:35Z"),
            doorbell.image_created_at_datetime,
        )
        self.assertEqual(
            "https://image.com/vmk16naaaa7ibuey7sar.jpg", doorbell.image_url
        )
        doorbell_motion_activity_no_image = DoorbellMotionActivity(
            json.loads(load_fixture("doorbell_motion_activity_no_image.json"))
        )
        self.assertFalse(
            update_doorbell_image_from_activity(
                doorbell, doorbell_motion_activity_no_image
            )
        )
        doorbell_motion_activity = DoorbellMotionActivity(
            json.loads(load_fixture("doorbell_motion_activity.json"))
        )
        self.assertTrue(
            update_doorbell_image_from_activity(doorbell, doorbell_motion_activity)
        )
        self.assertEqual(
            dateutil.parser.parse("2020-02-20T17:44:45Z"),
            doorbell.image_created_at_datetime,
        )
        self.assertEqual("https://my.updated.image/image.jpg", doorbell.image_url)
        old_doorbell_motion_activity = DoorbellMotionActivity(
            json.loads(load_fixture("doorbell_motion_activity_old.json"))
        )
        # returns false we send an older activity
        self.assertFalse(
            update_doorbell_image_from_activity(doorbell, old_doorbell_motion_activity)
        )
        self.assertEqual(
            dateutil.parser.parse("2020-02-20T17:44:45Z"),
            doorbell.image_created_at_datetime,
        )
        self.assertEqual("https://my.updated.image/image.jpg", doorbell.image_url)
        wrong_doorbell_motion_activity = DoorbellMotionActivity(
            json.loads(load_fixture("doorbell_motion_activity_wrong.json"))
        )

        with self.assertRaises(ValueError):
            update_doorbell_image_from_activity(
                doorbell, wrong_doorbell_motion_activity
            )

    def test_update_doorbell_image_from_activity_missing_image_at_start(self):
        doorbell = DoorbellDetail(
            json.loads(load_fixture("get_doorbell_missing_image.json"))
        )
        self.assertEqual("K98GiDT45GUL", doorbell.device_id)
        self.assertEqual(
            None, doorbell.image_created_at_datetime,
        )
        self.assertEqual(None, doorbell.image_url)
        doorbell_motion_activity_no_image = DoorbellMotionActivity(
            json.loads(load_fixture("doorbell_motion_activity_no_image.json"))
        )
        self.assertFalse(
            update_doorbell_image_from_activity(
                doorbell, doorbell_motion_activity_no_image
            )
        )
        doorbell_motion_activity = DoorbellMotionActivity(
            json.loads(load_fixture("doorbell_motion_activity.json"))
        )
        self.assertTrue(
            update_doorbell_image_from_activity(doorbell, doorbell_motion_activity)
        )
        self.assertEqual(
            dateutil.parser.parse("2020-02-20T17:44:45Z"),
            doorbell.image_created_at_datetime,
        )
        self.assertEqual("https://my.updated.image/image.jpg", doorbell.image_url)
