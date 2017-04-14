# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corecluster', '0028_task_version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='version',
            field=models.TextField(default='15.10', max_length=16),
        ),
    ]
