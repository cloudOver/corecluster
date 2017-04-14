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


from netaddr import IPNetwork
from django.db import models
from corecluster.models.core.subnet import Subnet
from corecluster.utils.exception import CoreException
from corenetwork.utils.logger import *
from corecluster.models.common_models import CoreModel, StateMixin, UserMixin

class NetworkPool(StateMixin, UserMixin, CoreModel):
    states = [
        'locked',
        'ok',
        'deleted',
    ]
    default_state = 'ok'
    modes = [
        'routed',   # Routed networking model
        'public',   # Public network for lease redirections
        'isolated', # Isolated network (managed by openvswitch+vlans or vpn)
    ]
    address = models.GenericIPAddressField()
    mask = models.PositiveIntegerField(help_text="Network mask in short format (e.g. 24 for 255.255.255.0 network)")
    mode = models.CharField(max_length=40, choices=[(k, k) for k in modes], default='public', help_text="Network mode.")

    serializable = ['id', 'address', 'mask', 'state', 'mode']

    def __unicode__(self):
        return "%s/%d" % (self.address, self.mask)


    def to_cidr(self):
        return self.address + "/" + str(self.mask)


    def to_ipnetwork(self):
        return IPNetwork(self.address + "/" + str(self.mask))


    def is_in_use(self):
        """
        Check if any vm uses this network
        """
        for net in self.subnet_set.all():
            if net.is_in_use():
                return True
        return False


    def release(self):
        """
        Removes all user networks from this network
        """
        if self.is_in_use():
            raise CoreException('network_in_use')

        for net in self.subnet_set.all():
            net.release()
            net.delete()


    def get_unused_ipnetwork(self, mask):
        """
        @returns Unused subnetwork represented by IPNetwork object
        """
        networks = []
        for network in self.subnet_set.all():
            networks.append(network.to_ipnetwork())
        networks = sorted(networks)

        if self.mask > mask:
            raise CoreException('network_to_large')

        if len(networks) == 0:
            return IPNetwork(self.address + '/' + str(mask))

        if IPNetwork(self.address + '/' + str(mask)).next().network <= networks[0].network:
            return IPNetwork(self.address + '/' + str(mask))

        # Find matching hole in existing networks
        for i in xrange(len(networks) - 1):
            n = IPNetwork(str(networks[i].next().network) + "/" + str(mask))
            if networks[i].next().network <= n.network and n.next().network <= networks[i + 1].network:
                return n

        # If previous fails, try to fit network at end of pool
        n = IPNetwork(str(networks[-1].next().network) + "/" + str(mask))
        if n.network <= networks[-1].network:
            # So, last network had smaller mask than requested network (and next, after last is still
            # before our requested new with given mask)
            n = n.next()
        if n.network <= self.to_ipnetwork().next().network:
            return n
        else:
            # or raise exception, if this is not possible
            raise CoreException('network_unavailable')

