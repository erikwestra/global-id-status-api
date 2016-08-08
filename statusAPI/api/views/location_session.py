""" statusAPI.api.views.location_session

    This module implements the /location_session endpoint for the Status API.
"""
import json
import traceback
import uuid

from django.http import (HttpResponseNotAllowed, HttpResponseForbidden,
                         HttpResponseNotFound, HttpResponse, JsonResponse)

from django.views.decorators.csrf import csrf_exempt

from statusAPI.shared.models import *
from statusAPI.shared.lib    import hmac, utils

#############################################################################

@csrf_exempt
def location_session(request, global_id):
    """ Respond to the "<global_id>/location_session" endpoint.
    """
    try:
        if request.method == "POST":
            return post_location_session(request, global_id)
        elif request.method == "DELETE":
            return delete_location_session(request, global_id)
        else:
            return HttpResponseNotAllowed(["POST", "DELETE"])
    except:
        traceback.print_exc()
        raise

#############################################################################

def post_location_session(request, global_id):
    """ Respond to an HTTP POST "<global_id>/location_session" API call.
    """
    # Check the HMAC authentication.

    access_id = utils.get_access_id(global_id)
    if access_id == None:
        return HttpResponseForbidden()

    if not hmac.check_hmac_authentication(request, access_id.access_secret):
        return HttpResponseForbidden()

    # Create a new location session for this user, re-using the old one if it
    # exists.

    try:
        session = LocationSession.objects.get(global_id__global_id=global_id)
    except LocationSession.DoesNotExist:
        session = None

    if session == None:
        session = LocationSession()
        session.global_id  = access_id.global_id
        session.session_id = uuid.uuid4().hex
        session.save()

    # Finally, return the session ID back to the caller.

    return JsonResponse({'session_id' : session.session_id}, status=201)

#############################################################################

def delete_location_session(request, global_id):
    """ Respond to an HTTP DELETE "<global_id>/location_session" API call.
    """
    # Check the HMAC authentication.

    access_id = utils.get_access_id(global_id)
    if access_id == None:
        return HttpResponseForbidden()

    if not hmac.check_hmac_authentication(request, access_id.access_secret):
        return HttpResponseForbidden()

    # Delete the location session for this user.

    try:
        session = LocationSession.objects.get(global_id__global_id=global_id)
    except LocationSession.DoesNotExist:
        return HttpResponseNotFound()

    session.delete()

    # Tell the user we succeeded.

    return HttpResponse(status=200)

