# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corecluster', '0031_related_tasks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lease',
            name='redirected',
            field=models.ForeignKey(related_name='redirected_set', to='corecluster.Lease', null=True),
        ),
    ]
