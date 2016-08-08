""" statusAPI.api.tests.test_location_session

    This module tests the /location_session endpoint for the Status API.
"""
import json
import uuid

from django.test  import TestCase
from django.utils import timezone

from statusAPI.shared.models import *

from statusAPI.shared.lib import hmac, utils
from . import apiTestHelpers

#############################################################################

class LocationSessionTestCase(TestCase):
    """ Unit tests for the "<global_id>/location_session" API endpoint.
    """
    def test_post_location_session(self):
        """ Test the logic of creating a new location session.
        """
        global_id = apiTestHelpers.create_unique_global_id()
        access_id = apiTestHelpers.create_access_id(global_id)

        url = "/" + global_id.global_id + "/location_session"

        headers = hmac.calc_hmac_headers(
                                method="POST",
                                url=url,
                                body="",
                                access_secret=access_id.access_secret)

        response = self.client.post(url,
                                    "",
                                    content_type="application/json",
                                    **headers)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Content-Type'], "application/json")

        data = json.loads(response.content.decode("utf-8"))

        self.assertIsInstance(data, dict)
        self.assertCountEqual(data.keys(), ["session_id"])
        session_id = data['session_id']

        try:
            session = LocationSession.objects.get(session_id=session_id)
        except:
            session = None

        self.assertNotEqual(session, None)
        self.assertEqual(session.global_id, global_id)


    def test_delete_location_session(self):
        """ Test that posting a status with a permission creates a view.
        """
        global_id = apiTestHelpers.create_unique_global_id()
        access_id = apiTestHelpers.create_access_id(global_id)

        session_id = uuid.uuid4().hex

        session = LocationSession()
        session.global_id  = global_id
        session.session_id = session_id
        session.save()

        url = "/" + global_id.global_id + "/location_session"

        headers = hmac.calc_hmac_headers(
                                method="DELETE",
                                url=url,
                                body="",
                                access_secret=access_id.access_secret)

        response = self.client.delete(url, **headers)

        self.assertEqual(response.status_code, 200)

        try:
            session = LocationSession.objects.get(session_id=session_id)
        except:
            session = None

        self.assertEqual(session, None)

