""" statusAPI.api.tests.test_permission

    This module tests the /permission endpoint for the Status API.
"""
import json
import uuid

from django.test  import TestCase
from django.utils import timezone

from statusAPI.shared.models import *

from statusAPI.shared.lib import hmac, utils
from . import apiTestHelpers

#############################################################################

class PermissionTestCase(TestCase):
    """ Unit tests for the "/permission" API endpoint.
    """
    def test_create_permission(self):
        """ Test the logic of creating a new permission.
        """
        global_id_1 = apiTestHelpers.create_unique_global_id()
        global_id_2 = apiTestHelpers.create_unique_global_id()
        access_id   = apiTestHelpers.create_access_id(global_id_1)

        request = {"access_type" : "CURRENT",
                   "global_id"   : global_id_2.global_id,
                   "status_type" : "availability/text"}

        url = "/" + global_id_1.global_id + "/permission"

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
            permission = Permission.objects.get(
                                        issuing_global_id=global_id_1,
                                        recipient_global_id=global_id_2,
                                        access_type="CURRENT",
                                        status_type="availability/text")
        except Permission.DoesNotExist:
            permission = None

        self.assertNotEqual(permission, None)

    # -----------------------------------------------------------------------

    def test_get_permissions(self):
        """ Test the logic of retrieving a user's permissions.
        """
        global_id_1 = apiTestHelpers.create_unique_global_id()
        global_id_2 = apiTestHelpers.create_unique_global_id()
        global_id_3 = apiTestHelpers.create_unique_global_id()
        access_id   = apiTestHelpers.create_access_id(global_id_1)

        permission = Permission()
        permission.issuing_global_id   = global_id_1
        permission.access_type         = Permission.ACCESS_TYPE_CURRENT
        permission.recipient_global_id = global_id_2
        permission.status_type         = "*"
        permission.save()

        permission = Permission()
        permission.issuing_global_id   = global_id_1
        permission.access_type         = Permission.ACCESS_TYPE_HISTORY
        permission.recipient_global_id = global_id_3
        permission.status_type         = "location/latlong"
        permission.save()

        url = "/" + global_id_1.global_id + "/permission"

        headers = hmac.calc_hmac_headers(
                                method="GET",
                                url=url,
                                body="",
                                access_secret=access_id.access_secret)

        response = self.client.get(url, **headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], "application/json")

        data = json.loads(response.content.decode("utf-8"))

        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

        if data[0]['access_type'] == "CURRENT":
            current_entry = data[0]
            history_entry = data[1]
        else:
            history_entry = data[0]
            current_entry = data[1]

        self.assertEqual(current_entry['access_type'], "CURRENT")
        self.assertEqual(current_entry['global_id'],   global_id_2.global_id)
        self.assertEqual(current_entry['status_type'], "*")

        self.assertEqual(history_entry['access_type'], "HISTORY")
        self.assertEqual(history_entry['global_id'],   global_id_3.global_id)
        self.assertEqual(history_entry['status_type'], "location/latlong")

    # -----------------------------------------------------------------------

    def test_delete_permission(self):
        """ Test the logic of deleting a permission.
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

        url = "/" + global_id_1.global_id + "/permission"

        headers = hmac.calc_hmac_headers(
                                method="DELETE",
                                url=url,
                                body="",
                                access_secret=access_id.access_secret)

        response = self.client.delete(url + "?access_type=CURRENT"
                                          + "&global_id="+global_id_2.global_id
                                          + "&status_type=*",
                                      **headers)

        self.assertEqual(response.status_code, 200)

