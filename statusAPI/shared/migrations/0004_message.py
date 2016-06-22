# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0003_auto_20160613_1500'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField()),
                ('message', models.TextField()),
                ('recipient', models.ForeignKey(related_name='+', to='shared.GlobalID')),
                ('sender', models.ForeignKey(related_name='+', to='shared.GlobalID')),
            ],
        ),
    ]
