""" statusAPI.shared.models

    This module defines the various database models for the statusAPI system.
"""
import datetime

from django.db import models
from django.conf import settings
import django.utils.timezone

#############################################################################

class GlobalID(models.Model):
    """ A unique global ID value.

        Each distinct global ID value will have a record in this table.
    """
    id        = models.AutoField(primary_key=True)
    global_id = models.TextField(db_index=True, unique=True)

#############################################################################

class AccessID(models.Model):
    """ An allocated access ID.

        Each copy of the client system must ask for one of these.  Note that we
        keep all previously-allocated access IDs for history purposes; for a
        given global ID, only the most recent access ID is applicable.
    """
    id            = models.AutoField(primary_key=True)
    global_id     = models.ForeignKey(GlobalID)
    device_id     = models.TextField()
    timestamp     = models.DateTimeField()
    access_id     = models.TextField()
    access_secret = models.TextField()

#############################################################################

class StatusUpdateType(models.Model):
    """ A type of status update.
    """
    id          = models.AutoField(primary_key=True)
    type        = models.TextField(unique=True)
    description = models.TextField()

#############################################################################

class StatusUpdate(models.Model):
    """ A posted status update.

        Note that we keen these status updates forever, forming a history of
        the various status updates posted over time.
    """
    id        = models.AutoField(primary_key=True)
    global_id = models.ForeignKey(GlobalID)
    type      = models.ForeignKey(StatusUpdateType)
    timestamp = models.DateTimeField(db_index=True)
    contents  = models.TextField()

#############################################################################

class Permission(models.Model):
    """ A permission.

        This gives a group of global IDs access to a given set of status
        updates.
    """
    ACCESS_TYPE_CURRENT = "CURRENT"
    ACCESS_TYPE_HISTORY = "HISTORY"
    ACCESS_TYPE_CHOICES = ((ACCESS_TYPE_CURRENT, "Current"),
                           (ACCESS_TYPE_HISTORY, "History"))

    id                  = models.AutoField(primary_key=True)
    issuing_global_id   = models.ForeignKey(GlobalID, related_name="+")
    access_type         = models.TextField(choices=ACCESS_TYPE_CHOICES)
    recipient_global_id = models.ForeignKey(GlobalID, related_name="+")
    status_type         = models.TextField() # May include wildcards.


    def matches_status_type(self, status_type):
        """ Return True if this permission matches the given status type.

            We compare the given status type against the 'status_type' field in
            our record, allowing for wildcards.  If the given status type is
            covered by this Permission record, we return True.
        """
        if self.status_type == "*":
            return True
        elif self.status_type.endswith("*"):
            if status_type.startswith(self.status_type[:-1]):
                return True
        else:
            if status_type == self.status_type:
                return True
        return False # no match.

#############################################################################

class CurrentStatusUpdateView(models.Model):
    """ A current status update that a given global ID can view.

        Whenever a status update gets posted, the poster's permissions are used
        to create a CurrentStatusUpdateView record for each global ID that is
        allowed to view that record.
    """
    id                  = models.AutoField(primary_key=True)
    issuing_global_id   = models.ForeignKey(GlobalID, related_name="+")
    recipient_global_id = models.ForeignKey(GlobalID, related_name="+")
    status_update       = models.ForeignKey(StatusUpdate)
    type                = models.ForeignKey(StatusUpdateType)
    timestamp           = models.DateTimeField()
    contents            = models.TextField()

#############################################################################

class Message(models.Model):
    """ A message being sent from one global ID to another.

        Note that these are temporary.
    """
    id        = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField()
    sender    = models.ForeignKey(GlobalID, related_name="+")
    recipient = models.ForeignKey(GlobalID, related_name="+")
    message   = models.TextField()

#############################################################################

class NonceValueManager(models.Manager):
    """ A custom manager for the NonceValue database table.
    """
    def purge(self):
        """ Delete all NonceValues older than settings.KEEP_NONCE_VALUES_FOR.
        """
        if settings.KEEP_NONCE_VALUES_FOR == None:
            return # Keep Nonce values forever.

        max_age = datetime.timedelta(days=settings.KEEP_NONCE_VALUES_FOR)
        cutoff  = django.utils.timezone.now() - max_age

        self.filter(timestamp__lte=cutoff).delete()

#############################################################################

class NonceValue(models.Model):
    """ A Nonce value that has been used to make an authenticated request.

        Note that we timestamp the Nonce values.  We delete old Nonce values to
        keep this database table to a reasonable size; the exact length of time
        we keep the Nonce values depends on a custom setting; the period needs
        to be long enough to ensure that HMAC-authenticated requests cannot be
        resent.  A period of a year is probably a good value.
    """
    id        = models.AutoField(primary_key=True)
    nonce     = models.TextField(db_index=True, unique=True)
    timestamp = models.DateTimeField()

    # Use our custom manager for the NonceValue class.

    objects = NonceValueManager()

