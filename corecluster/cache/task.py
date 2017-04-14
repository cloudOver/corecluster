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


import importlib

from corenetwork.utils.logger import log
from corecluster.utils.exception import CoreException
from corecluster.models.common_models import CoreModel
from corecluster.cache.model import Model
from corecluster.cache import Cache


from corenetwork.utils import config


class Task(Model):
    states = [
        'init',
        'not active',
        'waiting',
        'start trigger',
        'in progress',
        'finish trigger',
        'ok',
        'failed',
        'canceled',
    ]

    serializable = ['id',
                    'data',
                    'type',
                    'action',
                    'version',
                    'ignore_errors',
                    'repeated',
                    'creation_time',
                    'start_time',
                    'modification_time',
                    'finish_time',
                    'comment',
                    'agent_id',
                    'user_id',
                    'state',
    ]

    container = 'tasks'

    state = 'init'
    data = {}
    action = ''
    ignore_errors = False
    repeated = 0

    start_time = None
    modification_time = None
    finish_time = None
    comment = ''
    agent_id = None
    user_id = None

    def __unicode__(self):
        return self.type + '-' + self.action + '-' + self.id


    def append_to(self, objects, broadcast=False):
        self.set_state('init')
        self.save()
        from corecluster.models.core.agent import Agent

        if broadcast:
            for agent in Agent.objects.filter(state='running').all():
                l = Cache.lock('Agent:' + str(agent.id) + ':lock')
                l.acquire()
                Cache.hset('Agent:' + str(agent.id), self.cache_key(), 'broadcast')
                l.release()

        for db_object in objects:
            l = Cache.lock('db:' + db_object.__class__.__name__ + ':' + db_object.id + ':lock')
            l.acquire()

            obj = db_object.__class__.objects.get(pk=db_object.id)
            if obj.last_task is not None:
                log(msg="Changing last task from %s to %s for ID %s" % (obj.last_task, self.cache_key(), obj.id),
                    tags=('agent', 'debug'),
                    context=self.logger_ctx)
                blockers = Cache.lrange('blockers:' + self.cache_key(), 0, Cache.llen('blockers:' + self.cache_key()))
                if obj.last_task not in blockers:
                    Cache.lpush('blockers:' + self.cache_key(), obj.last_task)
                obj.last_task = self.cache_key()
            else:
                obj.last_task = self.cache_key()
                obj.save()

            # Update task list related to this object
            props = obj.get_all_props()
            if not 'tasks' in props:
                props['tasks'] = []
            props['tasks'].append(self.cache_key())

            # Delete non-existing tasks related to this object
            active_tasks = Cache.hkeys(self.container)
            new_tasks = []
            for task in props['tasks']:
                if task in active_tasks:
                    new_tasks.append(task)
            props['tasks'] = new_tasks

            # Save changes in object
            obj.set_all_props(props)
            obj.save()

            l.release()

        for obj in objects:
            setattr(self, obj.__class__.__name__ + '_id', obj.id)
            setattr(self, obj.__class__.__name__ + '_module', obj.__class__.__module__)
            assert isinstance(obj, CoreModel)
            self.serializable.append(obj.__class__.__name__ + '_id')
            self.serializable.append(obj.__class__.__name__ + '_module')

        self.set_state('not active')
        self.save()


    def delete(self):
        while True:
            if Cache.lpop('blockers:' + self.cache_key()) is None:
                break
        super(Task, self).delete()


    def get_obj(self, model):
        try:
            module = importlib.import_module(getattr(self, model + '_module'))
            cls = getattr(module, model)
            return cls.objects.get(pk=getattr(self, model + '_id'))
        except Exception as e:
            log(msg='Failed to get related object: %s for task %s:%s' % (model, self.type, self.action),
                context=self.logger_ctx,
                exception=e)


    def has_prop(self, key):
        return key in self.data


    def get_prop(self, key, default=None):
        try:
            if key in self.data:
                return self.data[key]
            else:
                return default
        except Exception as e:
            raise CoreException(str(e))


    def get_all_props(self):
        return self.data


    def set_prop(self, key, value):
        self.data[key] = value


    def set_all_props(self, props):
        self.data = props


    @staticmethod
    def _has_blockers(blockers):
        for blocker in blockers:
            task_type = blocker.split(':')[1]
            if blocker in Cache.hkeys(Task.container + ':' + task_type)\
                    and Cache.hget(Task.container + ':' + task_type, blocker) not in config.get('agent', 'IGNORE_TASKS'):
                return True
        return False


    @staticmethod
    def get_task(type, actions, agent=None):

        # First, check agent's queue for new tasks (Tasks related to this queue are atomic)
        if agent is not None:
            l = Cache.lock('Agent:' + str(agent.id)+ ':lock')
            l.acquire()
            keys = Cache.hkeys('Agent:' + str(agent.id))
            if len(keys) > 0:
                Cache.hdel('Agent:' + str(agent.id), *keys)
            l.release()

            bcasted = []
            for id in keys:
                task = Task(data=Cache.hget(Task.container, id))

                if task.action not in actions:
                    continue

                if not Task._has_blockers(Cache.lrange('blockers:' + task.cache_key(), 0, Cache.llen('blockers:' + task.cache_key()))):
                    task.set_state('waiting')
                    task.save(skip_lock=True)

                    bcasted.append(task)
                else:
                    Cache.hset('Agent:' + str(agent.id), task.cache_key(), 'broadcast')
            if len(bcasted) > 0:
                return bcasted

        # Then check global queue for this kind of agent
        l = Cache.lock(Task.container + ':' + type + ':lock')
        l.acquire()
        keys = (Cache.hkeys(Task.container + ':' + type))

        for id in keys:
            _state = Cache.hget(Task.container + ':' + type, id)
            if _state != 'not active':
                continue

            task = Task(data=Cache.hget(Task.container, id))

            if task.action not in actions:
                continue

            if not Task._has_blockers(Cache.lrange('blockers:' + task.cache_key(), 0, Cache.llen('blockers:' + task.cache_key()))):
                task.set_state('waiting')
                task.save(skip_lock=True)

                l.release()
                return [task]
            else:
                task.set_state('not active')
                task.save(skip_lock=True)

        l.release()

        return []


    @staticmethod
    def get_related(object, state=states):
        return []

        # return [task for task in object.related_tasks.filter(state__in=state)]
