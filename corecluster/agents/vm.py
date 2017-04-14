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


import libvirt
import threading
from corecluster.agents.base_agent import BaseAgent
from corecluster.exceptions.agent import *
from corenetwork.utils.logger import log


class AgentThread(BaseAgent):
    task_type = 'vm'
    supported_actions = ['create', 'shutdown', 'poweroff', 'reset', 'remove_vm', 'start_vm']

    def __init__(self):
        threading.Thread.__init__(self)

    def task_failed(self, task, exception):
        if not task.ignore_errors:
            vm = task.get_obj('VM')
            vm.set_state('failed')
            vm.save()
        super(AgentThread, self).task_failed(task, exception)


    def create(self, task):
        vm = task.get_obj('VM')
        vm.set_state('init')
        vm.save()

        vm.node.check_online(task.ignore_errors)

        conn = vm.node.libvirt_conn()

        try:
            vm_template = vm.libvirt_template
        except Exception as e:
            conn.close()
            raise TaskError('vm_template', e)


        try:
            conn.defineXML(vm_template)
        except Exception as e:
            conn.close()
            log(msg="Cannot define libvirt domain", exception=e, tags=('vm', 'agent', 'error'), context=task.logger_ctx)
            raise TaskError('vm_define', e)

        vm = task.get_obj('VM')
        vm.set_state('stopped')
        vm.save()
        conn.close()


    def shutdown(self, task):
        vm = task.get_obj('VM')

        if not vm.in_states(['running']):
            return

        vm.node.check_online(task.ignore_errors)

        conn = vm.node.libvirt_conn()

        try:
            domain = conn.lookupByName(vm.libvirt_name)
            domain.shutdown()
        except:
            vm = task.get_obj('VM')
            vm.set_state('stopped')
            vm.save()

        conn.close()


    def poweroff(self, task):
        vm = task.get_obj('VM')

        if not vm.in_states(['running']):
            return

        vm.node.check_online(task.ignore_errors)

        conn = vm.node.libvirt_conn()

        try:
            domain = conn.lookupByName(vm.libvirt_name)
            domain.destroy()
        except:
            vm = task.get_obj('VM')
            vm.set_state('stopped')
            vm.save()

        conn.close()


    def reset(self, task):
        vm = task.get_obj('VM')

        if not vm.in_states(['running']):
            raise TaskError('vm_not_running')

        vm.node.check_online(task.ignore_errors)

        vm = task.get_obj('VM')
        vm.state = 'reseting'
        vm.save()

        conn = vm.node.libvirt_conn()

        try:
            domain = conn.lookupByName(vm.libvirt_name)
            domain.reset(0)

            vm = task.get_obj('VM')
            vm.set_state('running')
            vm.save()
        except Exception as e:
            log(msg="Cannot reset domain", exception=e, tags=('vm', 'agent', 'error'), context=task.logger_ctx)
            raise TaskError('vm_reset_failed', e)

        conn.close()


    def remove_vm(self, task):
        vm = task.get_obj('VM')

        vm.node.check_online(task.ignore_errors)

        conn = vm.node.libvirt_conn()

        try:
            domain = conn.lookupByName(vm.libvirt_name)
            if domain.info()[0] == libvirt.VIR_DOMAIN_RUNNING:
                domain.destroy()
            domain.undefine()
        except Exception as e:
            log(msg="Failed to undefine and destroy domain. Skipping", exception=e, tags=('vm', 'agent', 'error'), context=task.logger_ctx)

        vm = task.get_obj('VM')
        vm.set_state('closed')
        vm.save()

        for device in vm.device_set.all():
            device.delete()

        conn.close()


    def start_vm(self, task):
        vm = task.get_obj('VM')

        if vm.in_states(['starting', 'running']):
            return
        elif not vm.in_states(['stopped']):
            raise TaskError('vm_not_stopped')

        vm.node.check_online(task.ignore_errors)

        vm = task.get_obj('VM')
        vm.set_state('starting')
        vm.save()

        conn = vm.node.libvirt_conn()

        try:
            domain = conn.lookupByName(vm.libvirt_name)
        except Exception as e:
            raise TaskError('vm_not_defined', e)

        try:
            domain.create()
            vm = task.get_obj('VM')
            vm.set_state('running')
            vm.libvirt_id = domain.ID()
            vm.save()
        except Exception as e:
            log(msg="Cannot start domain", exception=e, tags=('vm', 'agent', 'error'), context=task.logger_ctx)
            raise TaskError('vm_start_failed', e)

        conn.close()
