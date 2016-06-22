""" statusAPI.api.tests.test_access

    This module tests the /access endpoint for the Status API.
"""
import json
import uuid

from django.test  import TestCase
from django.utils import timezone

from statusAPI.shared.models import *

from statusAPI.shared.lib import hmac
from . import apiTestHelpers

#############################################################################

class AccessTestCase(TestCase):
    """ Unit tests for the "/access" API endpoint.
    """
    def test_obtain_new_access_id(self):
        """ Test the logic of obtaining a new access ID.
        """
        global_id = apiTestHelpers.create_unique_global_id()
        device_id = apiTestHelpers.random_string()

        request = {'global_id' : global_id.global_id,
                   'device_id' : device_id}

        response = self.client.post("/access",
                                    json.dumps(request),
                                    content_type="application/json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Content-Type'], "application/json")

        data = json.loads(response.content.decode("utf-8"))

        self.assertIsInstance(data, dict)
        self.assertCountEqual(data.keys(), ["access_id", "access_secret"])


    def test_get_access_token_again(self):
        """ Test the logic of re-obtaining an access token.
        """
        global_id = apiTestHelpers.create_unique_global_id()
        device_id = apiTestHelpers.random_string()

        access_id = AccessID()
        access_id.global_id     = global_id
        access_id.device_id     = device_id
        access_id.timestamp     = timezone.now()
        access_id.access_id     = uuid.uuid4().hex
        access_id.access_secret = uuid.uuid4().hex
        access_id.save()

        request = {'global_id' : global_id.global_id,
                   'device_id' : device_id}

        response = self.client.post("/access",
                                    json.dumps(request),
                                    content_type="application/json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Content-Type'], "application/json")

        data = json.loads(response.content.decode("utf-8"))

        self.assertIsInstance(data, dict)
        self.assertCountEqual(data.keys(), ["access_id", "access_secret"])
        self.assertEqual(data['access_id'],     access_id.access_id)
        self.assertEqual(data['access_secret'], access_id.access_secret)


    def test_change_device_id(self):
        """ Check that it is forbidden to change a device ID.
        """
        global_id = apiTestHelpers.create_unique_global_id()

        # Generate two random (but different) device IDs.

        while True:
            device_id_1 = apiTestHelpers.random_string()
            device_id_2 = apiTestHelpers.random_string()

            if device_id_1 == device_id_2:
                continue
            else:
                break

        # Create an access ID record for the first device ID.

        access_id = AccessID()
        access_id.global_id     = global_id
        access_id.device_id     = device_id_1
        access_id.timestamp     = timezone.now()
        access_id.access_id     = uuid.uuid4().hex
        access_id.access_secret = uuid.uuid4().hex
        access_id.save()

        # Now ask the API to generate an access ID for the same global ID but a
        # different device ID.  This should fail.

        request = {'global_id' : global_id.global_id,
                   'device_id' : device_id_2}

        response = self.client.post("/access",
                                    json.dumps(request),
                                    content_type="application/json")

        self.assertEqual(response.status_code, 403) # Forbidden.

        # Check that the access ID has not been updated.

        access_id = AccessID.objects.get(id=access_id.id)

        self.assertEqual(access_id.device_id, device_id_1)

