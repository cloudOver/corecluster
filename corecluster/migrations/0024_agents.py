# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import corecluster.models.common_models


class Migration(migrations.Migration):

    dependencies = [
        ('corecluster', '0023_reorder_hardware'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('_data', models.TextField(default=b'{}', help_text=b'Additional data. Leave blank if not used')),
                ('id', models.CharField(default=corecluster.models.common_models.id_generator, max_length=36, serialize=False, primary_key=True, help_text=b'API id used to identify all objects in Core')),
                ('state', models.CharField(max_length=30)),
                ('type', models.CharField(max_length=30)),
                ('pid', models.IntegerField()),
                ('hostname', models.CharField(max_length=64)),
                ('tasks_processed', models.IntegerField(default=0)),
                ('tasks_failed', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='task',
            name='agent',
            field=models.ForeignKey(blank=True, to='corecluster.Agent', null=True),
        ),
    ]