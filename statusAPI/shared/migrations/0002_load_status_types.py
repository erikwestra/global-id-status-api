""" 0002_load_status_types

    This data migration adds the set of known status types to the database.
"""
from django.db import models, migrations

#############################################################################

def add_status_types(apps, schema_editor):
    """ Add the status types to the database.
    """
    StatusUpdateType = apps.get_model("shared", "StatusUpdateType")

    status_type = StatusUpdateType()
    status_type.type = "availability/text"
    status_type.description = "Is the owner of this global ID available " \
                            + "for work?"
    status_type.save()

    status_type = StatusUpdateType()
    status_type.type = "location/latlong"
    status_type.description = "The global ID's current location"
    status_type.save()

#############################################################################

def remove_status_types(apps, schema_editor):
    """ Remove the status types from the database.
    """
    StatusUpdateType = apps.get_model("shared", "StatusUpdateType")
    StatusUpdateType.objects.all().delete()

#############################################################################

class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_status_types,
                             reverse_code=remove_status_types)
    ]

