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
from corecluster.models.core.subnet import Subnet

class Cmd(CommandLineBase):
    actions = {
        'list': {
            'help': 'List subnets',
        },
        'delete': {
            'help': 'Remove network if not in use'
        },
        'lease_list': {
            'help': 'List leases in network'
        },
    }

    def list(self):
        print "ID\t\t\t\t\tUser\t\t\t\t\tAddress\t\tMode\tPool"
        for un in Subnet.objects.all():
            print "%s\t%s\t%s/%d\t%s\t%s/%d" % (un.id, un.user.id, un.address, un.mask, un.network_pool.mode, un.network_pool.address, un.network_pool.mask)

    def delete(self, id):
        un = Subnet.objects.get(pk=id)
        if not un.is_in_use():
            print "Scheduling network %s delete" % un.id
            un.release()
        else:
            print "Network is in use"

    def lease_list(self, id):
        un = Subnet.objects.get(pk=id)
        print "ID\t\t\t\t\tVM Address\tVM"
        for lease in un.lease_set.all():
            print "%s\t%s\t%s" % (lease.id, lease.vm_address, str(lease.vm))
