""" statusAPI.api.views.permission

    This module implements the /permission endpoint for the Status API.
"""
import json
import traceback
import urllib.parse

from django.http import (HttpResponseNotAllowed, HttpResponseForbidden,
                         HttpResponseBadRequest, HttpResponse, JsonResponse,
                         HttpResponseNotFound)

from django.views.decorators.csrf import csrf_exempt

from statusAPI.shared.models import *
from statusAPI.shared.lib    import hmac, utils

#############################################################################

@csrf_exempt
def permission(request, global_id):
    """ Respond to the "<global_id>/permission" endpoint.
    """
    try:
        if request.method == "GET":
            return get_permission(request, global_id)
        elif request.method == "POST":
            return post_permission(request, global_id)
        elif request.method == "DELETE":
            return delete_permission(request, global_id)
        else:
            return HttpResponseNotAllowed(["GET", "POST", "DELETE"])
    except:
        traceback.print_exc()
        raise

#############################################################################

def get_permission(request, global_id):
    """ Respond to the HTTP GET "<global_id>/permission" endpoint.
    """
    # Check the HMAC authentication.

    access_id = utils.get_access_id(global_id)
    if access_id == None:
        return HttpResponseForbidden()

    if not hmac.check_hmac_authentication(request, access_id.access_secret):
        return HttpResponseForbidden()

    # Get our query-string parameters.

    if "global_id" in request.GET:
        global_id_param = request.GET['global_id']
    else:
        global_id_param = None

    if "type" in request.GET:
        type_param = request.GET['type']
    else:
        type_param = None

    # Build a database query to retrieve the desired set of permissions.

    query = Permission.objects.filter(issuing_global_id=access_id.global_id)

    if global_id_param != None:
        query = query.filter(recipient_global_id__global_id=global_id_param)

    # Build a list of the matching permissions.

    permissions = []
    for permission in query:
        if type_param != None:
            # Only include the permission if it covers the given type of status
            # update.
            if not permission.matches_status_type(type_param):
                continue

        permissions.append(
            {'access_type' : permission.access_type,
             'global_id'   : permission.recipient_global_id.global_id,
             'status_type' : permission.status_type})

    # Finally, return the results back to the caller.

    return JsonResponse(permissions, safe=False)

############################################################################

def post_permission(request, global_id):
    """ Respond to the HTTP POST "<global_id>/permission" endpoint.
    """
    # Check the HMAC authentication.

    access_id = utils.get_access_id(global_id)
    if access_id == None:
        return HttpResponseForbidden()

    if not hmac.check_hmac_authentication(request, access_id.access_secret):
        return HttpResponseForbidden()

    # Get our request parameters.

    if request.META['CONTENT_TYPE'] != "application/json":
        return HttpResponse(status=415) # Unsupported media type.

    try:
        request_data = json.loads(request.body.decode("utf-8"))
    except ValueError:
        return HttpResponseBadRequest("Invalid JSON request")

    if "access_type" in request_data:
        access_type = request_data['access_type']
    else:
        return HttpResponseBadRequest("Invalid JSON request")

    if "global_id" in request_data:
        global_id = request_data['global_id']
    else:
        return HttpResponseBadRequest("Invalid JSON request")

    if "status_type" in request_data:
        status_type = request_data['status_type']
    else:
        return HttpResponseBadRequest("Invalid JSON request")

    # Check that the parameters are valid.

    if access_type not in ["CURRENT", "HISTORY"]:
        return HttpResponseBadRequest("Invalid access_type")

    if "*" in status_type and not status_type.endswith("*"):
        return HttpResponseBadRequest("Invalid status_type")

    # If necessary, create a GlobalID record for the recipient.

    global_id_rec,created = GlobalID.objects.get_or_create(global_id=global_id)

    # Create the new permission.

    permission = Permission()
    permission.issuing_global_id   = access_id.global_id
    permission.access_type         = access_type
    permission.recipient_global_id = global_id_rec
    permission.status_type         = status_type
    permission.save()

    # Finally, tell the caller the good news.

    return HttpResponse(status=201)

#############################################################################

def delete_permission(request, global_id):
    """ Respond to the HTTP DELETE "<global_id>/permission" endpoint.
    """
    # Check the HMAC authentication.

    access_id = utils.get_access_id(global_id)
    if access_id == None:
        return HttpResponseForbidden()

    if not hmac.check_hmac_authentication(request, access_id.access_secret):
        return HttpResponseForbidden()

    # Get our request parameters.  Note that, because Django doesn't parse our
    # query-string parameters, we have to do it manually.

    params = urllib.parse.parse_qs(request.META['QUERY_STRING'])

    if "access_type" not in params or len(params['access_type']) != 1:
        return HttpResponseBadRequest("Missing or invalid access_type")
    else:
        access_type = params['access_type'][0]

    if "global_id" not in params or len(params['global_id']) != 1:
        return HttpResponseBadRequest("Missing or invalid global_id")
    else:
        global_id = params['global_id'][0]

    if "status_type" not in params or len(params['status_type']) != 1:
        return HttpResponseBadRequest("Missing or invalid status_type")
    else:
        status_type = params['status_type'][0]

    # Delete the given permission, if it exists.

    Permission.objects.filter(issuing_global_id=access_id.global_id,
                              access_type=access_type,
                              recipient_global_id__global_id=global_id,
                              status_type=status_type).delete()

    return HttpResponse(status=200)

