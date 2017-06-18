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
import libvirt
import sys

class Cmd(CommandLineBase):
    actions = {
        'list': {
            'help': 'List nodes',
        },
        'info': {
            'help': 'Print information about node'
        },
        'disable': {
            'help': 'Disable and lock node'
        },
        'enable': {
            'help': 'Enable node, mount all resources and check'
        },
        'suspend': {
            'help': 'Suspend node'
        },
        'wakeup': {
            'help': 'Wakeup node by wakeonlan command'
        },
    }

    def list(self):
        print "ID\t\t\t\t\tAddress\t\tState\tRunning VMs"
        for node in Node.objects.all():
            print "%s\t%s\t%s\t%d" % (node.id, node.address, node.state, len(node.vm_set.exclude(state='closed')))

    def info(self, id):
        node = Node.objects.get(pk=id)
        for vm in node.vm_set.all():
            print "vm %s in state %s" % (vm.id, vm.state)
            for lease in vm.lease_set.all():
                print "    lease %s mode %s libvirt %s ip %s" % (lease.id, lease.subnet.network_pool.mode, lease.vm_ifname, lease.vm_address)
            for image in vm.image_set.all():
                print "    image %s dev %s" % (image.id, image.disk_dev)

    def disable(self, id):
        node = Node.objects.get(pk=id)
        print "Disabling node %s" % node.address
        node.stop()
        node.set_state('lock')
        node.save()

    def enable(self, id):
        node = Node.objects.get(pk=id)
        print "Enabling node %s" % node.address
        node.start()

    def suspend(self, id):
        node = Node.objects.get(pk=id)

        print "Canceling all not active tasks for node %s" % node.id
        for task in Task.get_related(node, ['not active']):
            task.set_state('canceled')
            task.save()

        print "Suspending node %s" % node.address
        task = Task()
        task.type = 'node'
        task.action = 'suspend'
        task.append_to([node])

    def wakeup(self, id):
        node = Node.objects.get(pk=id)
        print "Waking up node %s" % node.address
        task = Task()
        task.type = 'node'
        task.action = 'wake_up'
        task.append_to([node])
