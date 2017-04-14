# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corecluster', '0027_task_owners'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='version',
            field=models.TextField(default=b'15.07.51', max_length=16),
            preserve_default=True,
        ),
    ]