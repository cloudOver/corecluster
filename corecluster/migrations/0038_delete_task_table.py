# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corecluster', '0037_network_quota'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='agent',
        ),
        migrations.RemoveField(
            model_name='task',
            name='blockers',
        ),
        migrations.RemoveField(
            model_name='task',
            name='group',
        ),
        migrations.RemoveField(
            model_name='task',
            name='related_tasks',
        ),
        migrations.RemoveField(
            model_name='task',
            name='user',
        ),
        migrations.RemoveField(
            model_name='agent',
            name='related_tasks',
        ),
        migrations.RemoveField(
            model_name='device',
            name='related_tasks',
        ),
        migrations.RemoveField(
            model_name='group',
            name='related_tasks',
        ),
        migrations.RemoveField(
            model_name='image',
            name='related_tasks',
        ),
        migrations.RemoveField(
            model_name='lease',
            name='related_tasks',
        ),
        migrations.RemoveField(
            model_name='networkpool',
            name='related_tasks',
        ),
        migrations.RemoveField(
            model_name='node',
            name='related_tasks',
        ),
        migrations.RemoveField(
            model_name='permission',
            name='related_tasks',
        ),
        migrations.RemoveField(
            model_name='role',
            name='related_tasks',
        ),
        migrations.RemoveField(
            model_name='storage',
            name='related_tasks',
        ),
        migrations.RemoveField(
            model_name='subnet',
            name='related_tasks',
        ),
        migrations.RemoveField(
            model_name='template',
            name='related_tasks',
        ),
        migrations.RemoveField(
            model_name='token',
            name='related_tasks',
        ),
        migrations.RemoveField(
            model_name='user',
            name='related_tasks',
        ),
        migrations.RemoveField(
            model_name='vm',
            name='related_tasks',
        ),
        migrations.AddField(
            model_name='agent',
            name='last_task',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='last_task',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='group',
            name='last_task',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='last_task',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='lease',
            name='last_task',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='networkpool',
            name='last_task',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='node',
            name='last_task',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='permission',
            name='last_task',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='role',
            name='last_task',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='storage',
            name='last_task',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='subnet',
            name='last_task',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='template',
            name='last_task',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='token',
            name='last_task',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='last_task',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='vm',
            name='last_task',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.DeleteModel(
            name='Task',
        ),
    ]
