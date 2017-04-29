# -*- coding: utf-8 -*-
# @COPYRIGHT_begin
#
# Copyright [2010-2014] Institute of Nuclear Physics PAN, Krakow, Poland
#           [2014-2015] Maciej Nabozny
#           [2015-2016] Marta Nabozny
#
# Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# @COPYRIGHT_end

"""
@author Maciej Nabożny <mn@mnabozny.pl>
"""

from django.db import models
from netaddr import IPNetwork, IPAddress
import corecluster.utils.validation as v
from corecluster.models.common_models import CoreModel, UserMixin
from corenetwork.utils.renderer import render
from corenetwork.utils import config


class Lease(UserMixin, CoreModel):
    address = models.GenericIPAddressField()
    subnet = models.ForeignKey('Subnet')
    vm = models.ForeignKey('VM', null=True, blank=True)
    redirected = models.ForeignKey('Lease', null=True, related_name='redirected_set')
    hostname = models.CharField(max_length=200, default='vm')

    proxy_enabled = models.BooleanField(default=False)
    proxy_port = models.IntegerField(default=80)

    def __unicode__(self):
        return self.address

    def _get_address(self):
        return self.vm_address

    def _get_gateway(self):
        return self.gateway_address

    def _get_mac(self):
        return self.mac

    def _get_redirections(self):
        return [r.address for r in self.redirected_set.all()]

    def _get_public_redirection(self):
        if self.redirected is not None:
            return self.redirected.to_dict
        else:
            return None

    serializable = ['id',
                    'data',
                    ['address', '_get_address'],
                    ['gateway', '_get_gateway'],
                    ['mac', '_get_mac'],
                    'hostname',
                    ['redirected_to', '_get_redirections'],
                    ['redirected_from', '_get_public_redirection'],
                    'subnet_id',
                    'vm_id',
                    'access',
                    'proxy_enabled',
                    'proxy_port']

    editable = [['access', v.in_list(UserMixin.object_access)],
                ['hostname', v.is_hostname()]]

    @property
    def gateway_address(self):
        """
        Return gateway address for routed network lease
        """
        if self.subnet.network_pool.mode == 'isolated':
            return self.subnet.get_prop('gateway', '')
        elif self.subnet.network_pool.mode == 'routed':
            network = IPNetwork('%s/30' % self.address)
            return str(network.network + 1)
        else:
            return ''

    @property
    def vm_address(self):
        """
        Return vm address for routed network lease
        """
        if self.subnet.network_pool.mode == 'routed':
            network = IPNetwork('%s/30' % self.address)
            return str(network.network + 2)
        else:
            return self.address

    @property
    def domain_name(self):
        return config.get('core', 'DNS_DOMAIN')

    @property
    def mac(self):
        ip_hex = '%08x' % IPAddress(self.address).value
        return '00:02:%s:%s:%s:%s' % (ip_hex[0:2], ip_hex[2:4], ip_hex[4:6], ip_hex[6:8])

    @property
    def redirection_ifname(self):
        """
        Return interface name for public lease redirection
        """
        return str('cr-%s' % self.id)[:config.get('network', 'IFACE_NAME_LENGTH')]

    @property
    def vm_ifname(self):
        """
        Return vm's interface name
        """
        return str('cn-%s' % self.id)[:config.get('network', 'IFACE_NAME_LENGTH')]

    @property
    def isolated_port_name(self):
        """
        Return interface name for isolated network, attached to vxlan tunnel. This tunnel is bridged with
        vm_ifname interface
        """
        return str('vx-%s' % str(self.subnet.v_id))[:config.get('network', 'IFACE_NAME_LENGTH')]

    def libvirt_xml(self):
        """
        Get libvirt's xml describing vm's interface
        """
        return render('networking/%s.xml' % self.subnet.network_pool.mode, {
            'lease': self,
            'vm': self.vm
        })

    def firewall_xml(self):
        """
        Return libvirt's firewall definition for lease in routed network
        """
        return render('networking/firewall.xml', {
            'lease': self,
            'vm': self.vm
        })
