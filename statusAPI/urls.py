""" statusAPI.urls

    This module defines the various URL configurations for the Status API
    system.
"""
from django.conf.urls import url

from statusAPI.api.views.access     import access
from statusAPI.api.views.permission import permission
from statusAPI.api.views.status     import status
from statusAPI.api.views.history    import history
from statusAPI.api.views.message    import message # for now.

#############################################################################

urlpatterns = [
    url(r'^access$',                                  access),
    url(r'^(?P<global_id>[a-zA-Z0-9_]+)/permission$', permission),
    url(r'^(?P<global_id>[a-zA-Z0-9_]+)/status$',     status),
    url(r'^(?P<global_id>[a-zA-Z0-9_]+)/history$',    history),
    url(r'^(?P<global_id>[a-zA-Z0-9_]+)/message$',    message), # for now.
]

