""" statusAPI.api.tests.test_history

    This module tests the /history endpoint for the Status API.
"""
import datetime
import json
import uuid

from django.test  import TestCase
from django.utils import timezone

from statusAPI.shared.models import *

from statusAPI.shared.lib import hmac, utils
from . import apiTestHelpers

#############################################################################

class HistoryTestCase(TestCase):
    """ Unit tests for the "/history" API endpoint.
    """
    def test_get_own_history(self):
        """ Test the logic of obtaining your own status history.
        """
        global_id  = apiTestHelpers.create_unique_global_id()
        access_id  = apiTestHelpers.create_access_id(global_id)
        contents_1 = apiTestHelpers.random_string()
        contents_2 = apiTestHelpers.random_string()

        status_type,created = StatusUpdateType.objects.get_or_create(
                                    type="available/text",
                                    defaults={'description' : "Description"})

        now = timezone.now()

        status_update = StatusUpdate()
        status_update.global_id = global_id
        status_update.type      = status_type
        status_update.timestamp = now - datetime.timedelta(seconds=1)
        status_update.contents  = contents_1
        status_update.save()

        status_update = StatusUpdate()
        status_update.global_id = global_id
        status_update.type      = status_type
        status_update.timestamp = now
        status_update.contents  = contents_2
        status_update.save()

        url = "/" + global_id.global_id + "/history"

        headers = hmac.calc_hmac_headers(
                                method="GET",
                                url=url,
                                body="",
                                access_secret=access_id.access_secret)

        response = self.client.get(url + "?global_id=" + global_id.global_id
                                       + "&type=available/text", **headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], "application/json")

        data = json.loads(response.content.decode("utf-8"))

        self.assertIsInstance(data, dict)
        self.assertCountEqual(data.keys(), ["updates", "more"])
        self.assertEqual(len(data['updates']), 2)

        update_1 = data['updates'][0]
        update_2 = data['updates'][1]

        timestamp_1 = utils.datetime_to_timestamp(now -
                                                  datetime.timedelta(seconds=1))
        timestamp_2 = utils.datetime_to_timestamp(now)

        self.assertIsInstance(update_1, dict)
        self.assertCountEqual(update_1.keys(), ["global_id",
                                                "type",
                                                "timestamp",
                                                "contents"])
        self.assertEqual(update_1['global_id'], global_id.global_id)
        self.assertEqual(update_1['type'],      "available/text")
        self.assertEqual(update_1['timestamp'], timestamp_2)
        self.assertEqual(update_1['contents'],  contents_2)

        self.assertIsInstance(update_2, dict)
        self.assertCountEqual(update_2.keys(), ["global_id",
                                                "type",
                                                "timestamp",
                                                "contents"])
        self.assertEqual(update_2['global_id'], global_id.global_id)
        self.assertEqual(update_2['type'],      "available/text")
        self.assertEqual(update_2['timestamp'], timestamp_1)
        self.assertEqual(update_2['contents'],  contents_1)


    def test_get_other_history(self):
        """ Test the logic of obtaining someone else's status history.
        """
        global_id_1 = apiTestHelpers.create_unique_global_id()
        global_id_2 = apiTestHelpers.create_unique_global_id()
        access_id   = apiTestHelpers.create_access_id(global_id_2)
        contents_1 = apiTestHelpers.random_string()
        contents_2 = apiTestHelpers.random_string()

        status_type,created = StatusUpdateType.objects.get_or_create(
                                    type="available/text",
                                    defaults={'description' : "Description"})

        now = timezone.now()

        status_update = StatusUpdate()
        status_update.global_id = global_id_1
        status_update.type      = status_type
        status_update.timestamp = now - datetime.timedelta(seconds=1)
        status_update.contents  = contents_1
        status_update.save()

        status_update = StatusUpdate()
        status_update.global_id = global_id_1
        status_update.type      = status_type
        status_update.timestamp = now
        status_update.contents  = contents_2
        status_update.save()

        permission = Permission()
        permission.issuing_global_id   = global_id_1
        permission.access_type         = Permission.ACCESS_TYPE_HISTORY
        permission.recipient_global_id = global_id_2
        permission.status_type         = "*"
        permission.save()

        url = "/" + global_id_2.global_id + "/history"

        headers = hmac.calc_hmac_headers(
                                method="GET",
                                url=url,
                                body="",
                                access_secret=access_id.access_secret)

        response = self.client.get(url + "?global_id=" + global_id_1.global_id
                                       + "&type=available/text", **headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], "application/json")

        data = json.loads(response.content.decode("utf-8"))

        self.assertIsInstance(data, dict)
        self.assertCountEqual(data.keys(), ["updates", "more"])
        self.assertEqual(len(data['updates']), 2)

        update_1 = data['updates'][0]
        update_2 = data['updates'][1]

        timestamp_1 = utils.datetime_to_timestamp(now -
                                                  datetime.timedelta(seconds=1))
        timestamp_2 = utils.datetime_to_timestamp(now)

        self.assertIsInstance(update_1, dict)
        self.assertCountEqual(update_1.keys(), ["global_id",
                                                "type",
                                                "timestamp",
                                                "contents"])
        self.assertEqual(update_1['global_id'], global_id_1.global_id)
        self.assertEqual(update_1['type'],      "available/text")
        self.assertEqual(update_1['timestamp'], timestamp_2)
        self.assertEqual(update_1['contents'],  contents_2)

        self.assertIsInstance(update_2, dict)
        self.assertCountEqual(update_2.keys(), ["global_id",
                                                "type",
                                                "timestamp",
                                                "contents"])
        self.assertEqual(update_2['global_id'], global_id_1.global_id)
        self.assertEqual(update_2['type'],      "available/text")
        self.assertEqual(update_2['timestamp'], timestamp_1)
        self.assertEqual(update_2['contents'],  contents_1)

