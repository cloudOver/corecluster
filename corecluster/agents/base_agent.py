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


import os
import time
import socket
import datetime
import threading

from corenetwork.hook_interface import HookInterface
from corenetwork.utils import config
from corenetwork.utils.logger import log

from corecluster.models.core.agent import Agent
from corecluster.cache.task import Task
from corecluster.utils.context import Context
from corecluster.exceptions.agent import *


class BaseAgent(threading.Thread):
    task_type = ''
    supported_actions = []
    timeout = 5
    i_am_running = True
    logger_ctx = Context()
    agent = None
    pid = None


    ''' Logger instance used to log thread informations, not related to any task. Initialized in init '''
    common_log = None


    def init(self):
        """
        Initialize agent before starting tasks. Override this method to use in proper agent. Call this method in
        overriden class' init.
        """
        self.agent = Agent()
        self.agent.type = self.task_type
        self.agent.pid = os.getpid()
        self.agent.hostname = socket.gethostname()
        self.agent.ssh_public_key = open('/var/lib/cloudOver/.ssh/id_rsa.pub').read()
        self.agent.save()
        log(msg="Starting agent %s:%s" % (self.task_type, self.agent.id), tags=('agent', self.task_type, 'info'))


    def cleanup(self):
        """
        Cleanup after agent. Override this method to use in proper agent.
        """
        log(msg="Stopping agent %s" % self.task_type, tags=('agent', self.task_type, 'info'))
        self.agent.set_state('done')
        self.agent.save()
        if config.get('agent', 'REMOVE_AGENTS_ON_DONE'):
            self.agent.delete()


    def get_tasks(self):
        """
        Default function to get list of tasks. Uses task_type field to determine which tasks should be handled by agent.
        Override it to define own method of retreiving tasks
        """
        return Task.get_task(self.task_type, self.supported_actions, self.agent)


    def _exec_hooks(self, task, moment='start'):
        """
        Execute hooks for task, where trigger_name is action to execute. Don't
        :param task: Task object which calls trigger
        :param moment: Defines if hook is executed before or after task execution. Supported values: start or finish
        """

        hooks = HookInterface.get_hooks('agent.%s.%s' % (task.type, task.action), 'agent')
        for hook in hooks:
            hook.task = task

            try:
                log(msg='Starting hook agent.%s.%s' % (task.type, task.action), tags=('agent', self.task_type, 'info'), context=task.logger_ctx)
                if moment == 'start':
                    hook.start()
                elif moment == 'finish':
                    hook.finish()
                else:
                    log(msg='Unsupported moment in hook: %s' % moment, tags=('agent', self.task_type, 'info'))
            except Exception as e:
                log(msg='Hook agent.%s.%s failed' % (task.type, task.action), tags=('agent', self.task_type, 'error'), exception=e, context=task.logger_ctx)
                task.comment = task.comment + '\n' + 'agent.%s.%s: Failed (%s)' % (task.type, task.action, str(e))
                task.save()


    def task_assigned(self, task):
        """
        This method is called after task is assigned to agent. If overriding, remember to call task_assigned in parent
        """
        log(msg="Assigning task (%s): %s, data: %s" % (task.action, task.id, task.data), tags=('agent', self.task_type, 'info'), context=task.logger_ctx)
        task.set_state('waiting')
        task.save()


    def task_started(self, task):
        """
        This method is called when task is being started. If overriding, remember to call task_started in parent
        """
        task.set_state('start trigger')
        task.start_time = datetime.datetime.now()
        task.save()

        log(msg="Starting task (%s): %s, data: %s" % (task.action, task.id, task.data), tags=('agent', self.task_type, 'info'), context=task.logger_ctx)

        self._exec_hooks(task, 'start')

        task.set_state('in progress')
        task.save()


    def task_finished(self, task):
        """
        This method is called when task is finished. If overriding, remember to call task_finished in parent
        """
        task.set_state('finish trigger')
        task.save()

        self._exec_hooks(task, 'finish')

        log(msg="Task finished (%s): %s, data: %s" % (task.action, task.id, task.data), tags=('agent', self.task_type, 'info'), context=task.logger_ctx)
        task.set_state('ok')
        task.finish_time = datetime.datetime.now()
        task.save()

        self.agent.tasks_processed = self.agent.tasks_processed + 1
        self.agent.save()

        if config.get('agent', 'REMOVE_TASKS_ON_DONE'):
            task.delete()


    def task_error(self, task, exception):
        """
        This method is called when task raises fatal error (exception)
        """
        log(msg="Task fatal error: %s" % task.action, exception=exception, tags=('agent', self.task_type, 'error'), context=task.logger_ctx)

        task.comment = task.comment + '\n' + str(exception)
        task.save()
        self.task_failed(task, exception)


    def task_failed(self, task, exception):
        """
        This method is called when task fails. If overriding, remember to call task_failed in parent. This method
        stores information about exception in comment field in task. If ignore_errors is True, it marks task as ok.
        """
        log(msg="Task failed error: %s" % task.action, exception=exception, tags=('agent', self.task_type, 'error'), context=task.logger_ctx)

        task.finish_time = datetime.datetime.now()
        task.comment = task.comment + '\n' + str(exception)
        if isinstance(exception, TaskBaseException) and exception.exception != None:
            task.comment = task.comment + ' (' + str(exception.exception) + ')'

        if not task.ignore_errors:
            task.set_state('failed')
        else:
            task.set_state('ok')
        task.save()

        self.agent.tasks_processed = self.agent.tasks_processed + 1
        self.agent.tasks_failed = self.agent.tasks_failed + 1
        self.agent.save()


    def task_delayed(self, task, exception):
        """
        This method is called, when task is not ready to start (e.g. is waiting for vm is stopped). Executed on
        TaskNotReady exception is thrown.
        """
        log(msg="Delaying task: %s" % task.action, exception=exception, tags=('agent', self.task_type, 'alert'), context=task.logger_ctx)
        task.set_state('not active')
        task.agent = None
        task.comment = task.comment + '\n' + str(exception)
        task.repeated = task.repeated + 1
        task.save()


    def run(self):
        self.init()

        self.agent.set_state('running')
        self.agent.task_fetch_timeout = config.get('agent', 'TASK_FETCH_INTERVAL', 20)
        self.agent.save()

        log(msg="Agent %s is running" % self.task_type, tags=('agent', self.task_type, 'info'))

        while self.i_am_running:
            tasks = []
            try:
                tasks = self.get_tasks()
                for task in tasks:
                    self.task_assigned(task)
            except Exception as e:
                log(msg="Cannot get tasks", exception=e, tags=('agent', self.task_type, 'critical'))
                continue

            for task in tasks:
                self.task_started(task)
                try:
                    action = getattr(self, task.action)
                    action(task)
                    self.task_finished(task)
                except TaskFatalError as e:
                    self.task_error(task, e)
                except TaskError as e:
                    self.task_failed(task, e)
                except TaskNotReady as e:
                    self.task_delayed(task, e)
                except Exception as e:
                    self.task_error(task, e)

            time.sleep(self.agent.get_prop('task_fetch_timeout', config.get('agent', 'TASK_FETCH_INTERVAL', 20)))

            self.agent = Agent.objects.get(pk=self.agent.id)

            if self.agent.in_states(['stopping', 'done']):
                self.i_am_running = False

            self.agent.alive = datetime.datetime.now()
            self.agent.save()

        self.agent.set_state('done')
        self.agent.save()
        self.cleanup()
