# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corecluster', '0034_rename_networking'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lease',
            old_name='user_network',
            new_name='subnet',
        ),
        migrations.RenameField(
            model_name='subnet',
            old_name='available_network',
            new_name='network_pool',
        ),
    ]
