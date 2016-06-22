""" statusAPI.api.views.message

    This module implements the /message endpoint for the Status API.

    NOTE: This is temporary, and will be deleted at some time in the future.
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
def message(request, global_id):
    """ Respond to the "<global_id>/status" endpoint.
    """
    try:
        if request.method == "GET":
            return get_message(request, global_id)
        elif request.method == "POST":
            return post_message(request, global_id)
        else:
            return HttpResponseNotAllowed(["GET", "POST"])
    except:
        traceback.print_exc()
        raise

#############################################################################

def get_message(request, global_id):
    """ Respond to an HTTP GET "<global_id>/message" API call.
    """
    # Check the HMAC authentication.

    access_id = utils.get_access_id(global_id)
    if access_id == None:
        return HttpResponseForbidden()

    if not hmac.check_hmac_authentication(request, access_id.access_secret):
        return HttpResponseForbidden()

    # Get the messages to return.  At the same time, remember the messages to
    # delete.

    message_ids = []
    messages    = []

    query = Message.objects.filter(recipient__global_id=global_id)

    for message in query.order_by("timestamp"):
        message_ids.append(message.id)
        messages.append({'sender'  : message.sender.global_id,
                         'message' : json.loads(message.message)})

    # Delete the messages we retrieved.

    for message_id in message_ids:
        Message.objects.filter(id=message_id).delete()

    # Finally, return the messages back to the caller.

    print("Returning messages: {}".format(json.dumps(messages)))

    return JsonResponse(messages, safe=False)

#############################################################################

def post_message(request, global_id):
    """ Respond to an HTTP POST "<global_id>/message" API call.
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

    if "recipient" not in request_data:
        return HttpResponseBadRequest("Missing recipient")
    else:
        recipient = request_data['recipient']

    if "message" not in request_data:
        return HttpResponseBadRequest("Missing message")
    else:
        message = request_data['message']

    # Create the message.

    recipient_rec,created = GlobalID.objects.get_or_create(global_id=recipient)

    message_rec = Message()
    message_rec.timestamp = utils.current_utc_timestamp()
    message_rec.sender    = access_id.global_id
    message_rec.recipient = recipient_rec
    message_rec.message   = json.dumps(message)
    message_rec.save()

    # Finally, tell the caller that we created the new message

    print("Created message {} from {} to {}".format(json.dumps(message),
                                                    access_id.global_id,
                                                    recipient_rec.global_id))

    return HttpResponse(status=201)

