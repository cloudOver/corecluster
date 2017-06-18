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
from corecluster.models.core.vm import VM
from corecluster.models.core.lease import Lease
from corecluster.cache.task import Task
import libvirt
import sys

class Cmd(CommandLineBase):
    actions = {
        'list': {
            'help': 'List virtual machines',
        },
        'info': {
            'help': 'Print information about virtual machine'
        },
        'erase': {
            'help': 'Erase all resources associated with instance and instance itself'
        },
        'save': {
            'help': 'Save instance\'s base image, if assigned'
        },
        'cleanup': {
            'help': 'Cleanup database. Remove information about all closed virtual machines. By default this action is called by cron once a week.'
        },
        'check': {
            'help': 'Check vm\'s state and update database. Usefull when node is struggling connectivity problems. This helps to make database and cluster state consistent after disasters'
        },
        'vnc': {},
        'proxy': {},
        'webvnc': {
            'params': {
                'id': {
                    'help': 'ID of virtual machine',
                }
            }
        },
    }

    def list(self):
        print "ID\t\t\t\t\tUser\t\t\t\t\tNode\tState"
        for vm in VM.objects.all():
            print "%s\t%s\t%s\t%s" % (vm.id, vm.user.id, vm.node.address, vm.state)

    def info(self, id):
        vm = VM.objects.get(pk=id)
        print "state %s" % vm.state
        print "template %s" % vm.template.name
        print "base_image %s" % (str(vm.base_image))
        for lease in vm.lease_set.all():
            print "lease %s mode %s libvirt %s ip %s" % (
                lease.id, lease.subnet.network_pool.mode, lease.vm_ifname, lease.vm_address)
        for image in vm.image_set.all():
            print "image %s dev %s" % (image.id, image.disk_dev)

    def erase(self, id):
        vm = VM.objects.get(pk=id)
        print "Erasing VM %s" % vm.id
        vm.cleanup(True)

    def save(self, id):
        vm = VM.objects.get(pk=id)
        if vm.base_image is None:
            print "VM %s has no base image" % vm.id
        else:
            print "Saving VM's base image"
            task = Task()
            task.action = 'save_image'
            task.type = 'node'
            task.append_to([vm, vm.base_image, vm.node])

    def cleanup(self):
        for vm in VM.objects.filter(state='closed').all():
            vm.delete()

    def check(self, id):
        self._become_cloudover()
        vm = VM.objects.get(pk=id)
        conn = vm.node.libvirt_conn()
        domain = conn.lookupByName(vm.libvirt_name)
        print "Domain state: %d" % domain.state()[0]
        if domain.state()[0] == libvirt.VIR_DOMAIN_RUNNING:
            vm.set_state('running')
            vm.save()
        else:
            vm.set_state('stopped')
            vm.save()

    def vnc(self, id):
        vm = VM.objects.get(pk=id)
        print str(vm.node.address) + ':' + str(vm.vnc_port)

    def proxy(self, id):
        lease = Lease.objects.get(pk=id)
        if lease == None or not lease.proxy_enabled or lease.subnet.network_pool.mode != 'routed':
            print ''
        else:
            sys.stdout.write('http://' + str(lease.vm_address) + ':' + str(lease.proxy_port) + '/')

    def webvnc(self, id):
        vm = VM.objects.get(pk=id)
        if vm.vnc_enabled:
            sys.stdout.write('http://' + str(vm.node.address) + ':1' + str(vm.vnc_port))
        else:
            sys.exit(1)
