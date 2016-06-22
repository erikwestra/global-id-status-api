""" statusAPI.api.test.apiTestHelpers

    This module define various utility functions for testing the Status API.
"""
import datetime
import random
import string
import uuid

from django.utils import timezone

from statusAPI.shared.models import *

#############################################################################

def random_string(min_length=5, max_length=10):
    """ Generate and return a string of random lowercase letters and digits.

        The returned string will consist only of lowercase letters and digits,
        and be between the given minimum and maximum length.
    """
    length = random.randint(min_length, max_length)
    chars = []
    for i in range(length):
        chars.append(random.choice(string.ascii_lowercase+string.digits))
    return "".join(chars)

#############################################################################

def create_unique_global_id():
    """ Create and return a new GlobalID object with a unique global ID.
    """
    while True:
        global_id = random_string()
        try:
            existing_id = GlobalID.objects.get(global_id=global_id)
        except GlobalID.DoesNotExist:
            existing_id = None

        if existing_id == None:
            break
        else:
            continue # Keep trying until we get a unique global_id.

    global_id_rec = GlobalID()
    global_id_rec.global_id = global_id
    global_id_rec.save()

    return global_id_rec

#############################################################################

def create_access_id(global_id=None):
    """ Create and return a new AccessID object.

        If 'global_id' is supplied, it should be a GlobalID object to use for
        this access ID.  Otherwise, a new unique GlobalID object will be
        created.
    """
    if global_id == None:
        global_id = create_unique_global_id()

    while True:
        device_id = random_string()

        try:
            access_id = AccessID.objects.get(global_id=global_id,
                                             device_id=device_id)
        except AccessID.DoesNotExist:
            access_id = None

        if access_id == None:
            break

    access_id = AccessID()
    access_id.global_id     = global_id
    access_id.device_id     = device_id
    access_id.timestamp     = timezone.now()
    access_id.access_id     = uuid.uuid4().hex
    access_id.access_secret = uuid.uuid4().hex
    access_id.save()

    return access_id

