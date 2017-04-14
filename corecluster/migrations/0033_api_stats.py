# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('corecluster', '0032_redirected_set'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='alive',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 1, 9, 58, 7, 966684), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='permission',
            name='execution_time',
            field=models.CharField(max_length=40, default='0:00:00', help_text=b'Total time spent on function execution. Divided by requests equals to average time'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='permission',
            name='requests',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='token',
            name='valid_to',
            field=models.DateTimeField(null=True),
        ),
    ]
