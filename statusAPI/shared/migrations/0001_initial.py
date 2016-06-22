# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccessID',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('device_id', models.TextField()),
                ('timestamp', models.DateTimeField()),
                ('access_id', models.TextField()),
                ('access_secret', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='CurrentStatusUpdateView',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('timestamp', models.DateTimeField()),
                ('contents', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='GlobalID',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('global_id', models.TextField(unique=True, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='NonceValue',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('nonce', models.TextField(unique=True, db_index=True)),
                ('timestamp', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('access_type', models.TextField(choices=[('CURRENT', 'Current'), ('HISTORY', 'History')])),
                ('status_type', models.TextField()),
                ('issuing_global_id', models.ForeignKey(related_name='+', to='shared.GlobalID')),
                ('recipient_global_id', models.ForeignKey(related_name='+', to='shared.GlobalID')),
            ],
        ),
        migrations.CreateModel(
            name='StatusUpdate',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('timestamp', models.DateTimeField()),
                ('contents', models.TextField()),
                ('global_id', models.ForeignKey(to='shared.GlobalID')),
            ],
        ),
        migrations.CreateModel(
            name='StatusUpdateType',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('type', models.TextField(unique=True)),
                ('description', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='statusupdate',
            name='type',
            field=models.ForeignKey(to='shared.StatusUpdateType'),
        ),
        migrations.AddField(
            model_name='currentstatusupdateview',
            name='issuing_global_id',
            field=models.ForeignKey(related_name='+', to='shared.GlobalID'),
        ),
        migrations.AddField(
            model_name='currentstatusupdateview',
            name='recipient_global_id',
            field=models.ForeignKey(related_name='+', to='shared.GlobalID'),
        ),
        migrations.AddField(
            model_name='currentstatusupdateview',
            name='status_update',
            field=models.ForeignKey(to='shared.StatusUpdate'),
        ),
        migrations.AddField(
            model_name='currentstatusupdateview',
            name='type',
            field=models.ForeignKey(to='shared.StatusUpdateType'),
        ),
        migrations.AddField(
            model_name='accessid',
            name='global_id',
            field=models.ForeignKey(to='shared.GlobalID'),
        ),
    ]
