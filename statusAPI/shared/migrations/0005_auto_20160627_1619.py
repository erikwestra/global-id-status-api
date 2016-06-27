# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0004_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='currentstatusupdateview',
            name='tz_offset',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='statusupdate',
            name='tz_offset',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
