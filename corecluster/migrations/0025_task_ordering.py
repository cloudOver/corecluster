# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corecluster', '0024_agents'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='image',
        ),
        migrations.RemoveField(
            model_name='task',
            name='lease',
        ),
        migrations.RemoveField(
            model_name='task',
            name='node',
        ),
        migrations.RemoveField(
            model_name='task',
            name='storage',
        ),
        migrations.RemoveField(
            model_name='task',
            name='user_network',
        ),
        migrations.RemoveField(
            model_name='task',
            name='vm',
        ),
        migrations.AddField(
            model_name='agent',
            name='last_task',
            field=models.ForeignKey(related_name='+', default=None, to='corecluster.Task', null=True),
        ),
        migrations.AddField(
            model_name='availablenetwork',
            name='last_task',
            field=models.ForeignKey(related_name='+', default=None, to='corecluster.Task', null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='last_task',
            field=models.ForeignKey(related_name='+', default=None, to='corecluster.Task', null=True),
        ),
        migrations.AddField(
            model_name='group',
            name='last_task',
            field=models.ForeignKey(related_name='+', default=None, to='corecluster.Task', null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='last_task',
            field=models.ForeignKey(related_name='+', default=None, to='corecluster.Task', null=True),
        ),
        migrations.AddField(
            model_name='lease',
            name='last_task',
            field=models.ForeignKey(related_name='+', default=None, to='corecluster.Task', null=True),
        ),
        migrations.AddField(
            model_name='node',
            name='last_task',
            field=models.ForeignKey(related_name='+', default=None, to='corecluster.Task', null=True),
        ),
        migrations.AddField(
            model_name='permission',
            name='last_task',
            field=models.ForeignKey(related_name='+', default=None, to='corecluster.Task', null=True),
        ),
        migrations.AddField(
            model_name='role',
            name='last_task',
            field=models.ForeignKey(related_name='+', default=None, to='corecluster.Task', null=True),
        ),
        migrations.AddField(
            model_name='storage',
            name='last_task',
            field=models.ForeignKey(related_name='+', default=None, to='corecluster.Task', null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='last_task',
            field=models.ForeignKey(related_name='+', default=None, to='corecluster.Task', null=True),
        ),
        migrations.AddField(
            model_name='template',
            name='last_task',
            field=models.ForeignKey(related_name='+', default=None, to='corecluster.Task', null=True),
        ),
        migrations.AddField(
            model_name='token',
            name='last_task',
            field=models.ForeignKey(related_name='+', default=None, to='corecluster.Task', null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='last_task',
            field=models.ForeignKey(related_name='+', default=None, to='corecluster.Task', null=True),
        ),
        migrations.AddField(
            model_name='usernetwork',
            name='last_task',
            field=models.ForeignKey(related_name='+', default=None, to='corecluster.Task', null=True),
        ),
        migrations.AddField(
            model_name='vm',
            name='last_task',
            field=models.ForeignKey(related_name='+', default=None, to='corecluster.Task', null=True),
        ),
    ]