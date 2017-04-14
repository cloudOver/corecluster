# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corecluster', '0020_help_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='modification_time',
            field=models.DateTimeField(default=None, auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='task',
            name='start_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]