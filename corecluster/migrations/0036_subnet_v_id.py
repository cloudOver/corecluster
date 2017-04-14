# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corecluster', '0035_rename_foreign_keys'),
    ]

    operations = [
        migrations.AddField(
            model_name='subnet',
            name='v_id',
            field=models.IntegerField(default=None, help_text=b'VLAN or VxLAN id. Used only with isolated network pools', null=True, blank=True),
        ),
    ]
