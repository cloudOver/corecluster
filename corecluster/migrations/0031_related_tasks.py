# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corecluster', '0030_task_repeat'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='agent',
            name='last_task',
        ),
        migrations.RemoveField(
            model_name='availablenetwork',
            name='last_task',
        ),
        migrations.RemoveField(
            model_name='device',
            name='last_task',
        ),
        migrations.RemoveField(
            model_name='group',
            name='last_task',
        ),
        migrations.RemoveField(
            model_name='image',
            name='last_task',
        ),
        migrations.RemoveField(
            model_name='lease',
            name='last_task',
        ),
        migrations.RemoveField(
            model_name='node',
            name='last_task',
        ),
        migrations.RemoveField(
            model_name='permission',
            name='last_task',
        ),
        migrations.RemoveField(
            model_name='role',
            name='last_task',
        ),
        migrations.RemoveField(
            model_name='storage',
            name='last_task',
        ),
        migrations.RemoveField(
            model_name='task',
            name='last_task',
        ),
        migrations.RemoveField(
            model_name='template',
            name='last_task',
        ),
        migrations.RemoveField(
            model_name='token',
            name='last_task',
        ),
        migrations.RemoveField(
            model_name='user',
            name='last_task',
        ),
        migrations.RemoveField(
            model_name='usernetwork',
            name='last_task',
        ),
        migrations.RemoveField(
            model_name='vm',
            name='last_task',
        ),
        migrations.AddField(
            model_name='agent',
            name='related_tasks',
            field=models.ManyToManyField(default=None, related_name='+', to='corecluster.Task', blank=True),
        ),
        migrations.AddField(
            model_name='availablenetwork',
            name='related_tasks',
            field=models.ManyToManyField(default=None, related_name='+', to='corecluster.Task', blank=True),
        ),
        migrations.AddField(
            model_name='device',
            name='related_tasks',
            field=models.ManyToManyField(default=None, related_name='+', to='corecluster.Task', blank=True),
        ),
        migrations.AddField(
            model_name='group',
            name='related_tasks',
            field=models.ManyToManyField(default=None, related_name='+', to='corecluster.Task', blank=True),
        ),
        migrations.AddField(
            model_name='image',
            name='related_tasks',
            field=models.ManyToManyField(default=None, related_name='+', to='corecluster.Task', blank=True),
        ),
        migrations.AddField(
            model_name='lease',
            name='related_tasks',
            field=models.ManyToManyField(default=None, related_name='+', to='corecluster.Task', blank=True),
        ),
        migrations.AddField(
            model_name='node',
            name='related_tasks',
            field=models.ManyToManyField(default=None, related_name='+', to='corecluster.Task', blank=True),
        ),
        migrations.AddField(
            model_name='permission',
            name='related_tasks',
            field=models.ManyToManyField(default=None, related_name='+', to='corecluster.Task', blank=True),
        ),
        migrations.AddField(
            model_name='role',
            name='related_tasks',
            field=models.ManyToManyField(default=None, related_name='+', to='corecluster.Task', blank=True),
        ),
        migrations.AddField(
            model_name='storage',
            name='related_tasks',
            field=models.ManyToManyField(default=None, related_name='+', to='corecluster.Task', blank=True),
        ),
        migrations.AddField(
            model_name='task',
            name='related_tasks',
            field=models.ManyToManyField(default=None, related_name='+', to='corecluster.Task', blank=True),
        ),
        migrations.AddField(
            model_name='template',
            name='related_tasks',
            field=models.ManyToManyField(default=None, related_name='+', to='corecluster.Task', blank=True),
        ),
        migrations.AddField(
            model_name='token',
            name='related_tasks',
            field=models.ManyToManyField(default=None, related_name='+', to='corecluster.Task', blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='related_tasks',
            field=models.ManyToManyField(default=None, related_name='+', to='corecluster.Task', blank=True),
        ),
        migrations.AddField(
            model_name='usernetwork',
            name='related_tasks',
            field=models.ManyToManyField(default=None, related_name='+', to='corecluster.Task', blank=True),
        ),
        migrations.AddField(
            model_name='vm',
            name='related_tasks',
            field=models.ManyToManyField(default=None, related_name='+', to='corecluster.Task', blank=True),
        ),
    ]
