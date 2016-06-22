# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0002_load_status_types'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statusupdate',
            name='timestamp',
            field=models.DateTimeField(db_index=True),
        ),
    ]
