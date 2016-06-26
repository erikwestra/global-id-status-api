""" statusAPI.api.views.status

    This module implements the /status endpoint for the Status API.
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
def status(request, global_id):
    """ Respond to the "<global_id>/status" endpoint.
    """
    try:
        if request.method == "GET":
            return get_status(request, global_id)
        elif request.method == "POST":
            return post_status(request, global_id)
        else:
            return HttpResponseNotAllowed(["GET", "POST"])
    except:
        traceback.print_exc()
        raise

#############################################################################

def get_status(request, global_id):
    """ Respond to an HTTP GET "<global_id>/status" API call.
    """
    # Check the HMAC authentication.

    access_id = utils.get_access_id(global_id)
    if access_id == None:
        return HttpResponseForbidden()

    if not hmac.check_hmac_authentication(request, access_id.access_secret):
        return HttpResponseForbidden()

    # Get our request parameters.

    if "own" in request.GET and request.GET['own'] == "1":
        param_own = True
    else:
        param_own = False

    if "global_id" in request.GET:
        param_global_id = request.GET['global_id']
    else:
        param_global_id = None

    if "type" in request.GET:
        param_type = request.GET['type']
    else:
        param_type = None

    if "since" in request.GET and request.GET['since'] != "ALL":
        try:
            param_since = utils.timestamp_to_datetime(requests.GET['since'])
        except ValueError:
            return HttpResponseBadRequest("Invalid 'since' value")
    else:
        param_since = None

    # Build the database query to retrieve the desired set of
    # CurrentStatusUpdateView records.

    query = CurrentStatusUpdateView.objects.all()

    if param_own:
        query = query.filter(issuing_global_id=access_id.global_id)
    else:
        query = query.filter(recipient_global_id=access_id.global_id)

    if param_global_id != None:
        query = query.filter(issuing_global_id__global_id=param_global_id)

    if param_type != None:
        query = query.filter(type__type=param_type)

    if param_since != None:
        query = query.filter(timestamp__gt=param_since)

    # Assemble the list of status updates which match our database query.

    updates = []
    latest  = None
    for view in query:
        updates.append(
                {'global_id' : view.issuing_global_id.global_id,
                 'type'      : view.type.type,
                 'timestamp' : utils.datetime_to_timestamp(view.timestamp),
                 'contents'  : view.contents})
        if latest == None or view.timestamp > latest:
            latest = view.timestamp

    # Calculate the 'since' value to use for retrieving only the new updates.

    if latest == None:
        since = "ALL"
    else:
        since = utils.datetime_to_timestamp(latest)

    # Finally, return the results back to the caller.

    return JsonResponse({'updates' : updates,
                         'since'   : since})

#############################################################################

def post_status(request, global_id):
    """ Respond to an HTTP POST "<global_id>/status" API call.
    """
    # Check the HMAC authentication.

    access_id = utils.get_access_id(global_id)
    if access_id == None:
        return HttpResponseForbidden()

    if not hmac.check_hmac_authentication(request, access_id.access_secret):
        return HttpResponseForbidden()

    # Get our parameters from the body of the request.

    if request.META['CONTENT_TYPE'] != "application/json":
        return HttpResponse(status=415) # Unsupported media type.

    try:
        request_data = json.loads(request.body.decode("utf-8"))
    except ValueError:
        return HttpResponseBadRequest("Invalid JSON request")

    if "type" in request_data:
        status_type = request_data['type']
    else:
        return HttpResponseBadRequest("Invalid JSON request")

    if "timestamp" in request_data:
        status_timestamp = request_data['timestamp']
    else:
        return HttpResponseBadRequest("Invalid JSON request")

    if "contents" in request_data:
        status_contents = request_data['contents']
    else:
        return HttpResponseBadRequest("Invalid JSON request")

    # Check that the parameters are valid.

    try:
        status_update_type = StatusUpdateType.objects.get(type=status_type)
    except StatusUpdateType.DoesNotExist:
        return HttpResponseBadRequest("Invalid type")

    try:
        timestamp = utils.timestamp_to_datetime(status_timestamp)
    except:
        return HttpResponseBadRequest("Invalid timestamp")

    # Based on the type of status update, validate the contents.

    if status_type == "location/latlong":
        try:
            contents = json.loads(status_contents)
        except ValueError:
            return HttpResponseBadRequest("Invalid lat/long contents")

        if not isinstance(contents, dict):
            return HttpResponseBadRequest("Invalid lat/long contents")

        if sorted(contents.keys()) != ["latitude", "longitude"]:
            return HttpResponseBadRequest("Invalid lat/long contents")

        if not isinstance(contents['latitude'], (int, float)):
            return HttpResponseBadRequest("Invalid latitude value")

        if contents['latitude'] < -90 or contents['latitude'] > 90:
            return HttpResponseBadRequest("Invalid latitude value")

        if not isinstance(contents['longitude'], (int, float)):
            return HttpResponseBadRequest("Invalid longitude value")

        if contents['longitude'] < -180 or contents['longitude'] > 180:
            return HttpResponseBadRequest("Invalid longitude value")

    # Create the status update itself.

    update = StatusUpdate()
    update.global_id = access_id.global_id
    update.type      = status_update_type
    update.timestamp = timestamp
    update.contents  = status_contents
    update.save()

    # Now, based upon the permissions, create a CurrentStatusUpdateView record
    # for each global ID able to view this status update.

    for permission in Permission.objects.filter(
                                    issuing_global_id=access_id.global_id,
                                    access_type=Permission.ACCESS_TYPE_CURRENT):
        if permission.matches_status_type(status_type):
            # Create a CurrentStatusUpdateView record for this recipient,
            # replacing the existing one if it exists.
            try:
                view = CurrentStatusUpdateView.objects.get(
                            issuing_global_id=access_id.global_id,
                            recipient_global_id=permission.recipient_global_id,
                            type=status_update_type)
            except CurrentStatusUpdateView.DoesNotExist:
                view = None

            if view != None:
                view.delete()

            view = CurrentStatusUpdateView()
            view.issuing_global_id   = access_id.global_id
            view.recipient_global_id = permission.recipient_global_id
            view.status_update       = update
            view.type                = status_update_type
            view.timestamp           = timestamp
            view.contents            = status_contents
            view.save()

    # Finally, tell the caller that we created the new status update.

    return HttpResponse(status=201)

