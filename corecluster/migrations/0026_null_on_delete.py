# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('corecluster', '0025_task_ordering'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='last_task',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, default=None, to='corecluster.Task', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='availablenetwork',
            name='last_task',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, default=None, to='corecluster.Task', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='device',
            name='last_task',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, default=None, to='corecluster.Task', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='group',
            name='last_task',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, default=None, to='corecluster.Task', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='image',
            name='last_task',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, default=None, to='corecluster.Task', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='lease',
            name='last_task',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, default=None, to='corecluster.Task', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='node',
            name='last_task',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, default=None, to='corecluster.Task', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='permission',
            name='last_task',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, default=None, to='corecluster.Task', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='role',
            name='last_task',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, default=None, to='corecluster.Task', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='storage',
            name='last_task',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, default=None, to='corecluster.Task', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='last_task',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, default=None, to='corecluster.Task', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='template',
            name='last_task',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, default=None, to='corecluster.Task', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='token',
            name='last_task',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, default=None, to='corecluster.Task', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='last_task',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, default=None, to='corecluster.Task', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='usernetwork',
            name='last_task',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, default=None, to='corecluster.Task', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='vm',
            name='last_task',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, default=None, to='corecluster.Task', null=True),
            preserve_default=True,
        ),
    ]