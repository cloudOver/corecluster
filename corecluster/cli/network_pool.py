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
from corecluster.models.core.network_pool import NetworkPool


class Cmd(CommandLineBase):
    actions = {
        'list': {
            'help': 'List nodes',
        },
        'list_subnets': {
            'help': 'List subnets in network pool'
        },
    }

    def list(self):
        print "ID\t\t\t\t\tMode\tAddress\tSubnets"
        for np in NetworkPool.objects.all():
            print "%s\t%s\t%s/%d\t%d" % (np.id, np.mode, np.address, np.mask, np.subnet_set.count())

    def list_subnets(self, id):
        np = NetworkPool.objects.get(pk=id)
        print "ID\t\t\t\t\tAddress"
        for sn in np.subnet_set.all():
            print "%s\t%s/%d" % (sn.id, sn.address, sn.mask)
