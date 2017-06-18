"""
Copyright (C) 2014-2017 cloudover.io ltd.
This file is part of the CloudOver.org project

Licensee holding a valid commercial license for this software may
use it in accordance with the terms of the license agreement
between cloudover.io ltd. and the licensee.

Alternatively you may use this software under following terms of
GNU Affero GPL v3 license:

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version. For details contact
with the cloudover.io company: https://cloudover.io/


This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.


You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from corenetwork.cli.cli_base import CommandLineBase
from corecluster.models.core.node import Node
from corecluster.cache.task import Task
from corecluster.cache import Cache


class Cmd(CommandLineBase):
    actions = {
        'list': {
            'help': 'List tasks',
        },
        'list_active': {
            'help': 'List active tasks',
        },
        'delete': {
            'help': 'Delete task(s)',
            'params': {
                'id': {
                    'help': 'Task selector. Pass id to delete one task. Use \'failed\' or \'done\' to delete all tasks in state failed or done. Use \'all\' to delete all tasks from all queues.'
                }
            }
        },
        'cleanup': {
            'help': 'Remove all done and caceled tasks from queue',
        },
        'cancel': {
            'help': 'Cancel one or all tasks in queue',
            'params': {
                'id': {
                    'help': 'Task selector. Pass id to delete one task. Use \'all\' to delete all tasks in queue',
                }
            }
        },
        'info': {
            'help': 'Print information about task'
        },
        'dump': {
            'help': 'Dump task in json format'
        },
        'restart': {
            'help': 'Restart task'
        },
    }


    def _print_blockers(self, task, indent=0):
        for blocker in task.blockers.all():
            print "  %s%s:%s:\t\t%s\t%s" % (' ' * indent, blocker.type, blocker.action, blocker.state, blocker.id)
            self._print_blockers(blocker, indent+2)

    def list(self):
        print('ID\t\t\t\t\tType\t\tAction\t\tState')
        tasks = [Task(data=t) for t in Cache.hvals(Task.container)]
        for task in tasks:
            print '%s\t%s\t\t%s\t\t%s' % (task.id, task.type, task.action, task.state)

    def list_active(self):
        print('ID\t\t\t\t\tType\t\tAction\t\tState')
        tasks = [Task(data=t) for t in Cache.hvals(Task.container)]
        for task in tasks:
            if task.state not in ['ok', 'canceled']:
                print '%s\t%s\t\t%s\t\t%s' % (task.id, task.type, task.action, task.state)

    def delete(self, id):
        tasks = [Task(data=t) for t in Cache.hvals(Task.container)]
        if id == 'all':
            for k in Cache.keys():
                print('Deleting %s' % k)
                Cache.delete(k)
        elif id == 'failed':
            for task in tasks:
                if task.state == 'failed':
                    print('Deleting task %s' % task)
                    task.delete()
        elif id == 'done':
            for task in tasks:
                if task.state in ['ok', 'canceled']:
                    task.delete()
        else:
            for task_id in Cache.hkeys(Task.container):
                if task_id.endswith(':' + id):
                    task = Task(cache_key=task_id)
                    task.delete()
                    return

    def cleanup(self):
        tasks = [Task(data=t) for t in Cache.hvals(Task.container)]
        for task in tasks:
            if task.state in ['ok', 'canceled']:
                task.delete()

    def cancel(self, id):
        tasks = [Task(data=t) for t in Cache.hvals(Task.container)]
        if id == 'all':
            for task in tasks:
                print "Deleting %s" % task.id
                task.set_state('canceled')
                task.save()
        else:
            for task_id in Cache.hkeys(Task.container):
                if task_id.endswith(':' + id):
                    task = Task(cache_key=task_id)
                    print "Canceling %s" % task.id
                    task.set_state('canceled')
                    task.save()
                    return

    def info(self, id):
        for task_id in Cache.hkeys(Task.container):
            if task_id.endswith(':' + id):
                task = Task(cache_key=task_id)

                print("ID: " + task.id)
                print("State: " + str(task.state))
                print("Blocked by: " + ', '.join(Cache.lrange('blockers:' + task.cache_key(), 0, Cache.llen('blockers:' + task.cache_key()))))
                print("Type: " + str(task.type) + "-" + str(task.action))
                print("Comments: " + str(task.comment))
                print("Data: " + str(task.data))
                if task.agent_id is not None:
                    print "Agent: " + str(task.agent_id)
                else:
                    print "Agent: None"
    def dump(self, id):
        for task_id in Cache.hkeys(Task.container):
            if task_id.endswith(':' + id):
                print Cache.hget(Task.container, task_id)

    def restart(self, id):
        tasks = [Task(data=t) for t in Cache.hvals(Task.container)]
        if id == 'all':
            for task in tasks:
                print "Restarting %s" % task.id
                task.set_state('not active')
                task.agent = None
                task.save()
        else:
            for task_id in Cache.hkeys(Task.container):
                if task_id.endswith(':' + id):
                    task = Task(cache_key=task_id)
                    task.set_state('not active')
                    task.agent = None
                    task.save()
                    return
