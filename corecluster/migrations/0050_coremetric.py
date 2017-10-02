# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-10-02 20:54
from __future__ import unicode_literals

import corecluster.models.common_models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corecluster', '0049_node_mac'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClusterID',
            fields=[
                ('_data', models.TextField(default=b'{}', help_text=b'Additional data. Leave blank if not used')),
                ('id', models.CharField(default=corecluster.models.common_models.id_generator, help_text=b'API id used to identify all objects in Core', max_length=36, primary_key=True, serialize=False)),
                ('last_task', models.CharField(max_length=128, null=True)),
                ('installation_id', models.CharField(default=corecluster.models.common_models.id_generator, max_length=150)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]