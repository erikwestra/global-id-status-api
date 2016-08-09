""" statusAPI.api.views.location

    This module implements the /location endpoint for the Status API.
"""
import json
import traceback

from django.http import (HttpResponseNotAllowed, HttpResponseForbidden,
                         HttpResponseBadRequest, HttpResponse, JsonResponse)

from django.views.decorators.csrf import csrf_exempt

from statusAPI.shared.models import *
from statusAPI.shared.lib    import hmac, utils

#############################################################################

@csrf_exempt
def location(request):
    """ Respond to the "/location" endpoint.
    """
    try:
        if request.method == "POST":
            return post_location(request)
        else:
            return HttpResponseNotAllowed(["POST"])
    except:
        traceback.print_exc()
        raise

#############################################################################

def post_location(request):
    """ Respond to an HTTP POST "location" API call.
    """
    # Get our parameters from the body of the request.

    if request.META['CONTENT_TYPE'] != "application/json":
        return HttpResponse(status=415) # Unsupported media type.

    try:
        request_data = json.loads(request.body.decode("utf-8"))
    except ValueError:
        return HttpResponseBadRequest("Invalid JSON request")

    if "session_id" in request_data:
        session_id = request_data['session_id']
    else:
        return HttpResponseBadRequest("Invalid JSON request")

    if "locations" in request_data:
        locations = request_data['locations']
    else:
        return HttpResponseBadRequest("Invalid JSON request")

    if not isinstance(locations, (list,tuple)):
        return HttpResponseBadRequest("Invalid JSON request")

    # Check that the session ID is valid.

    try:
        session = LocationSession.objects.get(session_id=session_id)
    except LocationSession.DoesNotExist:
        return HttpResponseForbidden()

    # Get the status type to use for our new status updates.

    status_type = "location/latlong"

    try:
        status_update_type = StatusUpdateType.objects.get(type=status_type)
    except StatusUpdateType.DoesNotExist:
        return HttpResponseBadRequest("Missing status type!")

    # Create a "presence" update for each received location.

    for location in locations:
        if not isinstance(location, dict):
            return HttpResponseBadRequest("Invalid location: " + repr(location))

        if "timestamp" in location:
            timestamp = location['timestamp']
        else:
            return HttpResponseBadRequest("Missing timestamp: " +
                                          repr(location))

        try:
            timestamp = utils.timestamp_to_datetime(timestamp)
        except:
            return HttpResponseBadRequest("Invalid timestamp")

        if "latitude" in location:
            latitude = location['latitude']
        else:
            return HttpResponseBadRequest("Missing latitude: " +
                                          repr(location))

        if not isinstance(latitude, (int, float)):
            return HttpResponseBadRequest("Invalid latitude value")

        if latitude < -90 or latitude > 90:
            return HttpResponseBadRequest("Invalid latitude value")

        if "longitude" in location:
            longitude = location['longitude']
        else:
            return HttpResponseBadRequest("Missing longitude: " +
                                          repr(location))

        if not isinstance(longitude, (int, float)):
            return HttpResponseBadRequest("Invalid longitude value")

        if longitude < -180 or longitude > 180:
            return HttpResponseBadRequest("Invalid longitude value")

        contents = json.dumps({'latitude'  : latitude,
                               'longitude' : longitude,
                               'type'      : "presence"})

        utc_datetime,tz_offset = utils.datetime_to_utc_and_timezone(timestamp)

        update = StatusUpdate()
        update.global_id = session.global_id
        update.type      = status_update_type
        update.timestamp = utc_datetime
        update.tz_offset = tz_offset
        update.contents  = contents
        update.save()

        # Based upon the permissions, create a CurrentStatusUpdateView record
        # for each global ID able to view this status update.

        for permission in Permission.objects.filter(
                                    issuing_global_id=session.global_id,
                                    access_type=Permission.ACCESS_TYPE_CURRENT):
            if permission.matches_status_type(status_type):
                # Create a CurrentStatusUpdateView record for this recipient,
                # replacing the existing one if it exists.

                CurrentStatusUpdateView.objects.filter(
                        issuing_global_id=session.global_id,
                        recipient_global_id=permission.recipient_global_id,
                        type=status_update_type).delete()

                view = CurrentStatusUpdateView()
                view.issuing_global_id   = session.global_id
                view.recipient_global_id = permission.recipient_global_id
                view.status_update       = update
                view.type                = status_update_type
                view.timestamp           = utc_datetime
                view.tz_offset           = tz_offset
                view.contents            = contents
                view.save()

    # Finally, tell the caller that we accepted all the new locations.

    return HttpResponse(status=201)

