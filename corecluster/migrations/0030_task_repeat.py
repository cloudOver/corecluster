# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corecluster', '0029_task_version'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='repeated',
            field=models.IntegerField(default=0, help_text=b'How many times task was re-executed'),
        ),
    ]
