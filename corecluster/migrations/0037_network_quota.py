# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corecluster', '0036_subnet_v_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='group',
            old_name='quota_redirections',
            new_name='quota_lease_public',
        ),
        migrations.AddField(
            model_name='group',
            name='quota_lease_routed',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='group',
            name='quota_network_isolated',
            field=models.IntegerField(default=0),
        ),
    ]
