""" statusAPI.api.tests.test_status

    This module tests the /status endpoint for the Status API.
"""
import json
import uuid

from django.test  import TestCase
from django.utils import timezone

from statusAPI.shared.models import *

from statusAPI.shared.lib import hmac, utils
from . import apiTestHelpers

#############################################################################

class StatusTestCase(TestCase):
    """ Unit tests for the "<global_id>/status" API endpoint.
    """
    def test_post_status(self):
        """ Test the logic of posting a status update.
        """
        global_id = apiTestHelpers.create_unique_global_id()
        access_id = apiTestHelpers.create_access_id(global_id)

        request = {"type"      : "availability/text",
                   "timestamp" : utils.current_utc_timestamp(),
                   "contents"  : "Available"}

        url = "/" + global_id.global_id + "/status"

        headers = hmac.calc_hmac_headers(
                                method="POST",
                                url=url,
                                body=json.dumps(request),
                                access_secret=access_id.access_secret)

        response = self.client.post(url,
                                    json.dumps(request),
                                    content_type="application/json",
                                    **headers)

        self.assertEqual(response.status_code, 201)


    def test_post_status_yields_view(self):
        """ Test that posting a status with a permission creates a view.
        """
        global_id_1 = apiTestHelpers.create_unique_global_id()
        global_id_2 = apiTestHelpers.create_unique_global_id()
        access_id   = apiTestHelpers.create_access_id(global_id_1)

        permission = Permission()
        permission.issuing_global_id   = global_id_1
        permission.access_type         = Permission.ACCESS_TYPE_CURRENT
        permission.recipient_global_id = global_id_2
        permission.status_type         = "*"
        permission.save()

        request = {"type"      : "availability/text",
                   "timestamp" : utils.current_utc_timestamp(),
                   "contents"  : "Available"}

        url = "/" + global_id_1.global_id + "/status"

        headers = hmac.calc_hmac_headers(
                                method="POST",
                                url=url,
                                body=json.dumps(request),
                                access_secret=access_id.access_secret)

        response = self.client.post(url,
                                    json.dumps(request),
                                    content_type="application/json",
                                    **headers)

        self.assertEqual(response.status_code, 201)

        try:
            view = CurrentStatusUpdateView.objects.get(
                                        issuing_global_id=global_id_1,
                                        recipient_global_id=global_id_2,
                                        type__type="availability/text")
        except CurrentStatusUpdateView.DoesNotExist:
            view = None

        self.assertNotEqual(view, None)


    def test_get_status(self):
        """ Test that the GET <global_id>/status" endpoint returns the views.
        """
        global_id_1 = apiTestHelpers.create_unique_global_id()
        global_id_2 = apiTestHelpers.create_unique_global_id()
        access_id   = apiTestHelpers.create_access_id(global_id_2)
        contents    = apiTestHelpers.random_string()

        status_type,created = StatusUpdateType.objects.get_or_create(
                                    type="available/text",
                                    defaults={'description' : "Description"})

        now = timezone.now()

        status_update = StatusUpdate()
        status_update.global_id = global_id_1
        status_update.type      = status_type
        status_update.timestamp = now
        status_update.contents  = contents
        status_update.save()

        view = CurrentStatusUpdateView()
        view.issuing_global_id   = global_id_1
        view.recipient_global_id = global_id_2
        view.status_update       = status_update
        view.type                = status_type
        view.timestamp           = now
        view.contents            = contents
        view.save()

        url = "/" + global_id_2.global_id + "/status"

        headers = hmac.calc_hmac_headers(
                                method="GET",
                                url=url,
                                body="",
                                access_secret=access_id.access_secret)

        response = self.client.get(url, **headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], "application/json")

        data = json.loads(response.content.decode("utf-8"))

        self.assertIsInstance(data, dict)
        self.assertCountEqual(data.keys(), ["updates", "since"])
        self.assertEqual(len(data['updates']), 1)

        update = data['updates'][0]

        self.assertIsInstance(update, dict)
        self.assertCountEqual(update.keys(),
                              ["global_id", "type", "timestamp", "contents"])
        self.assertEqual(update['global_id'], global_id_1.global_id)
        self.assertEqual(update['type'], status_type.type)
        self.assertEqual(utils.timestamp_to_datetime(update['timestamp']), now)
        self.assertEqual(update['contents'], contents)

