# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corecluster', '0021_task_modification_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='template',
            name='hdd',
            field=models.IntegerField(default=10000, help_text=b'Maximum base image size in megabytes'),
            preserve_default=False,
        ),
    ]