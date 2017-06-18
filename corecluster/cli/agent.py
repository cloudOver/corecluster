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
from corecluster.models.core.agent import Agent

class Cmd(CommandLineBase):
    actions = {
        'list': {
            'help': 'List agents',
        },
        'info': {
            'help': 'Print information about agent'
        },
        'shutdown': {
            'help': 'Shutdown one or all agents'
        },
        'check': {
            'help': 'Mark all agents insative for more than two hours as inactive'
        },
        'cleanup': {
            'help': 'Remove all shutting down and stopping agents from database',
        }
    }

    def list(self):
        print "ID\t\t\t\t\tType\t\tPID\tHostname\t\tState"
        for agent in Agent.objects.all():
            print "%s\t%s\t\t%d\t%s\t%s" % (agent.id, agent.type, agent.pid, agent.hostname, agent.state)

    def info(self, id):
        node = Node.objects.get(pk=id)
        for vm in node.vm_set.all():
            print "vm %s in state %s" % (vm.id, vm.state)
            for lease in vm.lease_set.all():
                print "    lease %s mode %s libvirt %s ip %s" % (lease.id, lease.subnet.network_pool.mode, lease.vm_ifname, lease.vm_address)
            for image in vm.image_set.all():
                print "    image %s dev %s" % (image.id, image.disk_dev)

    def shutdown(self, id):
        if id == 'all':
            for agent in Agent.objects.filter(state='running'):
                print "Shutting down agent %s:%d (ID:%s)" % (agent.type, agent.pid, agent.id)
                agent.set_state('stopping')
                agent.save()
        else:
            agent = Agent.objects.get(pk=id)
            print "Shutting down agent %s:%d (ID:%s)" % (agent.type, agent.pid, agent.id)
            agent.set_state('stopping')
            agent.save()

    def check(self):
        for agent in Agent.objects.filter(alive__lt=datetime.now() - timedelta(hours=2)):
            agent.set_state('done')
            agent.save()

    def cleanup(self):
        for agent in Agent.objects.filter(state__in=['stopping', 'done']):
            agent.delete()
