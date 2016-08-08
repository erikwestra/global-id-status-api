""" statusAPI.api.tests.test_location

    This module tests the /location endpoint for the Status API.
"""
import json
import random
import uuid

from django.test  import TestCase
from django.utils import timezone

from statusAPI.shared.models import *

from statusAPI.shared.lib import hmac, utils
from . import apiTestHelpers

#############################################################################

class LocationTestCase(TestCase):
    """ Unit tests for the "/location" API endpoint.
    """
    def test_post_location(self):
        """ Test the logic of creating a new location session.
        """
        global_id = apiTestHelpers.create_unique_global_id()
        access_id = apiTestHelpers.create_access_id(global_id)

        session_id = uuid.uuid4().hex

        session = LocationSession()
        session.global_id  = global_id
        session.session_id = session_id
        session.save()

        location = {'timestamp' : utils.current_utc_timestamp(),
                    'latitude'  : random.randrange(-90, +90),
                    'longitude' : random.randrange(-180, +180)}

        request = {'session_id' : session_id,
                   'locations'  : [location]}

        url = "/location"

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

