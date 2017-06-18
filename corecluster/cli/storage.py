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
from corecluster.models.core.storage import Storage
from corecluster.cache.task import Task
from corecluster.models.core.node import Node


class Cmd(CommandLineBase):
    actions = {
        'list': {
            'help': 'List nodes',
        },
        'lock': {
            'help': 'Lock storage on core and all nodes'
        },
        'unlock': {
            'help': 'Unlock storage and mount at all nodes'
        },
    }

    def list(self):
        print "ID\t\t\t\t\tState\tTransport\tAddress\t\tDir\tName\tImages"
        for s in Storage.objects.all():
            print "%s\t%s\t%s\t\t%s\t%s\t%s\t%d" % (
            s.id, s.state, s.transport, s.address, s.dir, s.name, len(s.image_set.filter(state='ok').all()))

    def lock(self, id):
        s = Storage.objects.get(pk=id)
        s.set_state('locked')
        s.save()

        mnt = Task()
        mnt.type = 'storage'
        mnt.action = 'umount'
        mnt.append_to([s])

        for node in Node.objects.filter(state='ok'):
            umount_ok = True
            for vm in node.vm_set.all():
                for image in vm.image_set.all():
                    if image.storage == s:
                        print("WARNING: VM %s at node %s uses selected storage!" % (vm.id, node.address))
                        umount_ok = False

            if umount_ok:
                mnt = Task()
                mnt.type = 'node'
                mnt.action = 'umount'
                mnt.append_to([s, node])

    def unlock(self, id):
        s = Storage.objects.get(pk=id)
        s.set_state('locked')
        s.save()

        mnt = Task()
        mnt.type = 'storage'
        mnt.action = 'mount'
        mnt.state = 'not active'
        mnt.append_to([s])

        for node in Node.objects.filter(state='ok'):
            node.set_state('offline')
            node.save()

        for node in Node.objects.filter(Q(state='ok') | Q(state='offline')):
            node.start()
