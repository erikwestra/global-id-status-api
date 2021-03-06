""" statusAPI.api.views.access

    This module implements the /access endpoint for the Status API.
"""
import json
import traceback
import urllib.parse
import uuid

from django.utils import timezone

from django.views.decorators.csrf import csrf_exempt

from django.http import (HttpResponseNotAllowed, HttpResponse,
                         HttpResponseBadRequest, JsonResponse,
                         HttpResponseForbidden)

from statusAPI.shared.models import *

#############################################################################

@csrf_exempt
def access(request):
    """ Respond to the /access endpoint.
    """
    try:
        if request.method == "POST":
            return post_access(request)
        elif request.method == "DELETE":
            return delete_access(request)
        else:
            return HttpResponseNotAllowed(["POST", "DELETE"])
    except:
        traceback.print_exc()
        raise

#############################################################################

def post_access(request):
    """ Respond to the POST /access API call.
    """
    # Get the submitted request parameters.

    if request.META['CONTENT_TYPE'] != "application/json":
        return HttpResponse(status=415) # Unsupported media type.

    try:
        request_data = json.loads(request.body.decode("utf-8"))
    except ValueError:
        return HttpResponseBadRequest("Invalid JSON request")

    if "global_id" in request_data:
        global_id = request_data['global_id']
    else:
        return HttpResponseBadRequest("Invalid JSON request")

    if "device_id" in request_data:
        device_id = request_data['device_id']
    else:
        return HttpResponseBadRequest("Invalid JSON request")

    # Get the GlobalID object for the supplied global ID, creating one if
    # necessary.

    global_id_rec,created = GlobalID.objects.get_or_create(global_id=global_id)

    # If we have an existing AccessID record with the same global ID and device
    # ID, return the previously-calculated values.

    try:
        access_id = AccessID.objects.get(global_id=global_id_rec,
                                         device_id=device_id)
    except AccessID.DoesNotExist:
        access_id = None

    if access_id != None:
        return JsonResponse({'access_id'     : access_id.access_id,
                             'access_secret' : access_id.access_secret},
                            status=201)
                           

    # If we have an existing AccessID record with that global ID but a
    # different device ID, we block this.

    try:
        access_id = AccessID.objects.get(global_id=global_id_rec)
    except AccessID.DoesNotExist:
        access_id = None

    if access_id != None and access_id.device_id != device_id:
        return HttpResponseForbidden()

    # If we get here, we are creating a new access ID for this user.  Do so.

    access_id = AccessID()
    access_id.global_id     = global_id_rec
    access_id.device_id     = device_id
    access_id.timestamp     = timezone.now()
    access_id.access_id     = uuid.uuid4().hex
    access_id.access_secret = uuid.uuid4().hex
    access_id.save()

    # Finally, return the details of the newly-created access ID back to the
    # caller.

    return JsonResponse({'access_id'     : access_id.access_id,
                         'access_secret' : access_id.access_secret},
                        status=201)

#############################################################################

def delete_access(request):
    """ Respond to the DELETE /access API endpoint.
    """
    # Get the submitted request parameters.

    params = urllib.parse.parse_qs(request.META['QUERY_STRING'])

    if "global_id" not in params or len(params['global_id']) != 1:
        return HttpResponseBadRequest()
    else:
        global_id = params['global_id'][0]

    # Get the GlobalID object for the supplied global ID, creating one if
    # necessary.

    global_id_rec,created = GlobalID.objects.get_or_create(global_id=global_id)

    # Delete the existing access credentials for this global ID, if it exists.

    AccessID.objects.filter(global_id=global_id_rec).delete()

    # Tell the caller that we succeeded.

    return HttpResponse(status=200)

