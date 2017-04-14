# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corecluster', '0038_delete_task_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='ssh_public_key',
            field=models.CharField(default=b'', max_length=1024),
        ),
    ]