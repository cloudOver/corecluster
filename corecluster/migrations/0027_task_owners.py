# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corecluster', '0026_null_on_delete'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='access',
            field=models.CharField(default=b'private', max_length=30, choices=[(b'private', b'private'), (b'public', b'public'), (b'group', b'group')]),
        ),
        migrations.AddField(
            model_name='task',
            name='group',
            field=models.ForeignKey(blank=True, to='corecluster.Group', null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='user',
            field=models.ForeignKey(blank=True, to='corecluster.User', null=True),
        ),
    ]