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


from django.db import models
from django.db.models import Q
from netaddr import IPNetwork

from corecluster.cache.task import Task
from corecluster.models.common_models import CoreModel, UserMixin
from corecluster.models.core.lease import Lease
from corecluster.utils.exception import CoreException
import corecluster.utils.validation as v
from corenetwork.utils import config
from corenetwork.utils.logger import log


class Subnet(UserMixin, CoreModel):
    address = models.GenericIPAddressField()
    mask = models.PositiveIntegerField()
    network_pool = models.ForeignKey('NetworkPool')
    name = models.CharField(max_length=200)
    is_isolated = models.BooleanField(default=False)

    v_id = models.PositiveIntegerField(null=True, blank=True, default=None, help_text="VLAN or VxLAN id. Used only with isolated network pools")

    def _get_total_leases(self):
        return self.lease_set.count()
    def _get_used_leases(self):
        return self._get_total_leases() - Lease.objects.filter(subnet=self).filter(Q(vm=None) | Q(vm__state='closed')).count()
    def _get_mode(self):
        return self.network_pool.mode

    serializable = ['id',
                    'data',
                    'address',
                    'mask',
                    'network_pool_id',
                    'name',
                    'access',
                    'is_isolated',
                    ['mode', '_get_mode'],
                    ['used_leases', '_get_used_leases'],
                    ['total_leases', '_get_total_leases']]

    editable = ['name', 'is_isolated',
                ['access', v.in_list(UserMixin.object_access)]]


    def __unicode__(self):
        return "%s/%d" % (self.address, self.mask)


    @property
    def isolated_port_name(self):
        '''
        Get name of port attached to vlan with isolated network. Don't use this interface to run any services. Instead
        use isolated_bridge_name interface to run any service.
        '''
        if self.network_pool.mode != 'isolated':
            raise CoreException('network_not_isolated')
        return str('ni-%s' % str(self.v_id))[:config.get('network', 'IFACE_NAME_LENGTH')]


    @property
    def isolated_bridge_name(self):
        '''
        Get name of bridge in isolated network namespace (connects vlan with veth pair and other devices). Use this
        interface to launch any services in isolated network (e.g. dhcp). Bridge with this name is present in
        both: default namespace and in network namespace related to this network.
        '''
        if self.network_pool.mode != 'isolated':
            raise CoreException('network_not_isolated')
        return str('cb-%s' % str(self.v_id))[:config.get('network', 'IFACE_NAME_LENGTH')]


    @property
    def isolated_veth_name(self):
        '''
        Get name of primary veth pair interface present in main network namespace. Don't use this interface for any
        services in your extensions
        '''
        if self.network_pool.mode != 'isolated':
            raise CoreException('network_not_isolated')
        return str('cp-%s' % self.v_id)[:config.get('network', 'IFACE_NAME_LENGTH')]


    @property
    def isolated_peer_name(self):
        '''
        Get name of secondary veth pair interface present in isolated network namespace. Don't use this interface for
        any services in your extensions
        '''
        if self.network_pool.mode != 'isolated':
            raise CoreException('network_not_isolated')
        return str('cq-%s' % self.v_id)[:config.get('network', 'IFACE_NAME_LENGTH')]


    @property
    def netns_name(self):
        '''
        Get network namespace name related to isolated network
        '''
        if self.network_pool.mode != 'isolated':
            raise CoreException('network_not_isolated')
        return str('ns-' + self.id)


    def to_cidr(self):
        return self.address + "/" + str(self.mask)


    def to_ipnetwork(self):
        return IPNetwork(self.address + "/" + str(self.mask))


    def is_in_use(self):
        for lease in self.lease_set.all():
            if lease.vm != None:
                return True
        return False


    @staticmethod
    def create_routed(context, address, mask, name, isolated):
        from corecluster.models.core.network_pool import NetworkPool

        if mask >= 30:
            raise CoreException('network_invalid_mask')

        for network_pool in NetworkPool.objects.filter(mode='routed').all():
            log(msg='Trying to allocate routed network in %s' % str(network_pool.to_ipnetwork()), context=context, tags=('network'))
            if network_pool.state == 'ok':
                try:
                    if address is None:
                        net = network_pool.get_unused_ipnetwork(mask)
                    else:
                        continue
                    log(msg=str(net), context=context, tags=('network'))

                    new_net = Subnet()
                    new_net.address = str(net.network)
                    new_net.mask = mask
                    new_net.name = name
                    new_net.network_pool = network_pool
                    new_net.user_id = context.user_id
                    new_net.is_isolated = isolated
                    new_net.save()

                    return new_net
                except Exception as e:
                    log(msg="Cannot find new net in %s" % network_pool.address, exception=e, context=context, tags=('network'))

        raise CoreException('network_not_available')


    @staticmethod
    def create_public(context, address, mask, name, isolated):
        from corecluster.models.core.network_pool import NetworkPool

        for network_pool in NetworkPool.objects.filter(mode='public').all():
            log(msg='Trying to allocate public network in %s' % str(network_pool.to_ipnetwork()), context=context, tags=('network'))
            if network_pool.state == 'ok':
                try:
                    if address is None:
                        net = network_pool.get_unused_ipnetwork(mask)
                    else:
                        continue
                    log(msg=str(net), context=context, tags=('network'))

                    new_net = Subnet()
                    new_net.address = str(net.network)
                    new_net.mask = mask
                    new_net.name = name
                    new_net.network_pool = network_pool
                    new_net.user_id = context.user_id
                    new_net.is_isolated = isolated
                    new_net.save()

                    return new_net
                except Exception as e:
                    log(msg="Cannot find new net in %s" % network_pool.address, exception=e, context=context, tags=('network'))

        raise CoreException('network_not_available')


    @staticmethod
    def create_isolated(context, address, mask, name):
        from corecluster.models.core.network_pool import NetworkPool

        try:
            IPNetwork('%s/%s' % (address, int(mask)))
        except:
            raise CoreException('network_address_is_invalid')

        new_net = None

        for network_pool in NetworkPool.objects.filter(mode='isolated').all():
            log(msg="for %s" % network_pool.id, context=context, tags=('network'))
            if IPNetwork('%s/%d' % (address, mask)) in network_pool.to_ipnetwork():
                v_id = 1
                ids = [subnet.v_id for subnet in network_pool.subnet_set.all()]
                while v_id in ids:
                    v_id += 1

                new_net = Subnet()
                new_net.address = address
                new_net.mask = mask
                new_net.name = name
                new_net.network_pool = network_pool
                new_net.user_id = context.user_id
                new_net.is_isolated = False
                new_net.v_id = v_id
                new_net.save()
                return new_net

            else:
                continue

        if new_net is None:
            raise CoreException('network_not_available')


    def prepare(self):
        t = Task()
        t.type = 'network'
        t.action = 'prepare'
        t.append_to([self])


    def allocate(self):
        """
        Create leases in Subnet
        """
        host_id = 0

        if self.network_pool.mode == 'isolated':
            raise CoreException('allocate_leases_manually')

        hosts = [h.address for h in self.lease_set.all()]

        while self.to_ipnetwork().network+host_id < self.to_ipnetwork().broadcast:
            host = self.to_ipnetwork().network+host_id
            if str(host) in hosts:
                host_id += 1
                continue

            if self.network_pool.mode == 'public':
                lease = Lease()
                lease.address = str(host)
                lease.subnet = self
                lease.user = self.user
                lease.save()
            elif self.network_pool.mode == 'routed':
                if host_id % 4 == 0:
                    lease = Lease()
                    lease.address = str(host)
                    lease.subnet = self
                    lease.user = self.user
                    lease.save()
            else:
                raise CoreException('unsupported_network_mode')

            host_id += 1


    def release(self):
        """
        Remove all leases from this network
        """
        if self.is_in_use():
            raise CoreException('network_in_use')

        for lease in self.lease_set.all():
            lease.delete()

        t = Task()
        t.type = 'network'
        t.action = 'delete'
        t.append_to([self])


    def get_unused(self):
        for lease in self.lease_set.all():
            if lease.vm == None:
                return lease
        raise CoreException('lease_not_found')
