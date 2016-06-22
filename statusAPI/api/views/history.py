""" statusAPI.api.views.history

    This module implements the /history endpoint for the Status API.
"""
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.http import (HttpResponseBadRequest, HttpResponseForbidden,
                         HttpResponseNotAllowed, JsonResponse)

from statusAPI.shared.lib    import hmac, utils
from statusAPI.shared.models import *

#############################################################################

MAX_PAGE_SIZE = 50 # Maximum number of status updates to return at once.

#############################################################################

@csrf_exempt
def history(request, global_id):
    """ Respond to the /history endpoint.
    """
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    # Check the HMAC authentication.

    access_id = utils.get_access_id(global_id)
    if access_id == None:
        return HttpResponseForbidden()

    if not hmac.check_hmac_authentication(request, access_id.access_secret):
        return HttpResponseForbidden()

    # Get our request parameters.

    if "global_id" in request.GET:
        global_id_param = request.GET['global_id']
    else:
        return HttpResponseBadRequest("Missing request params")

    if "type" in request.GET:
        type_param = request.GET['type']
    else:
        return HttpResponseBadRequest("Missing request params")

    if "more" in request.GET:
        more_param = request.GET['more']
    else:
        more_param = None

    # Check that the request is valid.

    try:
        status_type = StatusUpdateType.objects.get(type=type_param)
    except StatusUpdateType.DoesNotExist:
        return HttpResponseBadRequest("Invalid type")

    if access_id.global_id.global_id != global_id_param:
        # The user is attempting to access someone else's history.  Make sure
        # the other user has created a Permission record to allow this.
        has_permission = False # initially.
        for permission in Permission.objects.filter(
                                issuing_global_id__global_id=global_id_param,
                                access_type=Permission.ACCESS_TYPE_HISTORY,
                                recipient_global_id=access_id.global_id):
            if permission.matches_status_type(type_param):
                has_permission = True
                break

        if not has_permission:
            return HttpResponseForbidden()

    if more_param != None:
        try:
            more_param = int(more_param)
        except ValueError:
            return HttpResponseBadRequest("Invalid more parameter")

    # Build the database query to retrieve the desired set of status updates.
    # Note that we use a Paginator to paginate the results.

    query = StatusUpdate.objects.filter(global_id__global_id=global_id_param,
                                        type=status_type)
    query = query.order_by("-timestamp")
    paginator = Paginator(query, MAX_PAGE_SIZE)

    if more_param != None:
        page_num = more_param
    else:
        page_num = 1

    if page_num > paginator.num_pages:
        updates = []
        more    = None
    else:
        updates = []
        for update in paginator.page(page_num):
            updates.append(
                {'global_id' : update.global_id.global_id,
                 'type'      : update.type.type,
                 'timestamp' : utils.datetime_to_timestamp(update.timestamp),
                 'contents'  : update.contents})

        if page_num < paginator.num_pages:
            more = str(page_num + 1)
        else:
            more = None

    # Finally, return the results back to the caller.

    return JsonResponse({'updates' : updates,
                         'more'    : more})

