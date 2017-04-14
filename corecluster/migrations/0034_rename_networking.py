# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corecluster', '0033_api_stats'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AvailableNetwork',
            new_name='NetworkPool'),
        migrations.RenameModel(
            old_name='UserNetwork',
            new_name='Subnet'),
    ]
