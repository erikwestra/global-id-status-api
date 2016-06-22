""" statusAPI.shared.lib.utils

    This module define various utility functions for the StatusAPI system.
"""
import datetime
import base64
import hashlib
import uuid

from django.utils import timezone, dateparse

from statusAPI.shared.models import *

#############################################################################

def get_access_id(global_id):
    """ Return the access ID currently associated with the given global ID.
    """
    try:
        return AccessID.objects.get(global_id__global_id=global_id)
    except AccessID.DoesNotExist:
        return None
    except AccessID.MultipleObjectsReturned:
        return None # Should never happen.

#############################################################################

def current_utc_timestamp():
    """ Return the current date and time as an RFC-3339 format string, in UTC.
    """
    return datetime_to_timestamp(datetime.datetime.now(timezone.utc))

#############################################################################

def datetime_to_timestamp(date_time):
    """ Convert the given datetime object into an RFC-3339 format string.

        'date_time' should be a datetime.datetime object with the appropriate
        timezone set.  We convert this value to a string in RFC-3339 format.
    """
    return date_time.astimezone().isoformat()

#############################################################################

def timestamp_to_datetime(timestamp):
    """ Convert the given RFC-3339 format string into a datetime object.
    """
    return dateparse.parse_datetime(timestamp)

