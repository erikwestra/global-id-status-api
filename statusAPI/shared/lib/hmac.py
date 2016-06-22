""" statusAPI.shared.lib.hmac

    This module define various utility functions for working with HMAC
    authentication.
"""
import base64
import hashlib
import uuid

from django.utils import timezone

from statusAPI.shared.models import *

#############################################################################

def calc_hmac_headers(method, url, body, access_secret):
    """ Return the HTTP headers to use for an HMAC-authenticated request.

        The parameters are as follows:

            'method'

                The HTTP method to use for this request.

            'url'

                The full URL for the desired endpoint, excluding the server
                name.

            'body'

                The body of the HTTP request, as a string.

            'access_secret'

                The access secret for the user we are making an authenticated
                request for.

        We calculate the HMAC authentication headers to use for making an
        authenticated request to the server.  The headers are returned in the
        form of a dictionary mapping header fields to values.
    """
    nonce       = uuid.uuid4().hex
    content_md5 = hashlib.md5(body.encode("utf-8")).hexdigest()
    parts       = [method, url, content_md5, nonce, access_secret]
    hmac_digest = hashlib.sha1("\n".join(parts).encode("utf-8")).hexdigest()
    hmac_base64 = base64.b64encode(hmac_digest.encode("utf-8"))

    return {'Authorization' : "HMAC " + hmac_base64.decode("utf-8"),
            'Content_MD5'   : content_md5,
            'Nonce'         : nonce}

#############################################################################

def normalize_request_headers(request):
    """ Normalize the request headers for the given HTTP request.

        The HTTP headers for the given request (in request.META) are converted
        to uppercase, and have the string "HTTP_" removed from the start.  This
        avoids problems with different headers while unit testing versus
        running the live system.

        Upon completion, we return a dictionary mapping normalized request
        headers to their associated values.
    """
    headers = {}
    for header in request.META.keys():
        normalized_header = header.upper()
        if normalized_header.startswith("HTTP_"):
            normalized_header = normalized_header[5:]
        headers[normalized_header] = request.META[header]
    return headers

#############################################################################

def has_hmac_headers(request):
    """ Return True if the given request includes HMAC-authentication headers.
    """
    headers = normalize_request_headers(request)
    if "AUTHORIZATION" not in headers: return False
    if "CONTENT_MD5"   not in headers: return False
    if "NONCE"         not in headers: return False
    return True

#############################################################################

def check_hmac_authentication(request, access_secret):
    """ Return True if the given request's HMAC-authentication is correct.

        The parameters are as follows:

            'request'

                An HttpRequest object for the current request.  This will
                include the HMAC-authentication headers.

            'access_secret'

                The access secret that should have been used to calculate the
                HMAC authentication headers.

        If the given request's HMAC-authentication headers are correct for the
        given access secret, we return True.
    """
    headers = normalize_request_headers(request)

    NonceValue.objects.purge()

    http_method      = request.method
    url              = request.path

    hmac_auth_string = headers.get("AUTHORIZATION")
    content_md5      = headers.get("CONTENT_MD5")
    nonce            = headers.get("NONCE")

    if hmac_auth_string == None or content_md5 == None or nonce == None:
#        logger.warn("HMAC auth failed due to missing HTTP headers.")
        return False

    if content_md5 != hashlib.md5(request.body).hexdigest():
#        logger.warn("HMAC auth failed due to incorrect Content-MD5 value.")
        return False

    # Check that the nonce value hasn't already been used, and remember it for
    # later.

    NonceValue.objects.purge()

    try:
        existing_nonce = NonceValue.objects.get(nonce=nonce)
    except NonceValue.DoesNotExist:
        existing_nonce = None

    if existing_nonce != None:
#        logger.warn("HMAC auth failed because nonce value was reused.")
        return False

    nonce_value = NonceValue()
    nonce_value.nonce     = nonce
    nonce_value.timestamp = timezone.now()
    nonce_value.save()

    # Calculate the HMAC-authentication digest, and check that it mathes the
    # digest value from the header.

    parts       = [request.method, request.path, content_md5,
                   nonce, access_secret]
    hmac_digest = hashlib.sha1("\n".join(parts).encode("utf-8")).hexdigest()
    hmac_base64 = base64.b64encode(hmac_digest.encode("utf-8"))

    if hmac_auth_string != "HMAC " + hmac_base64.decode("utf-8"):
#        logger.warn("HMAC auth failed because authorization hash " +
#                    "doesn't match.")
        return False

    # If we get here, the HMAC authentication succeeded.  Whew!

    return True

