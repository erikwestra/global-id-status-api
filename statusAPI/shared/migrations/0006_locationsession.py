# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0005_auto_20160627_1619'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocationSession',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('session_id', models.TextField(db_index=True)),
                ('global_id', models.ForeignKey(related_name='+', to='shared.GlobalID')),
            ],
        ),
    ]
