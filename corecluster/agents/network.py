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


from corecluster.models.core import Lease, Device
from corecluster.agents.base_agent import BaseAgent
from corecluster.exceptions.agent import *
from corenetwork.utils.logger import log
from corenetwork.utils import system
from corenetwork.utils import config


class AgentThread(BaseAgent):
    """
    Networking agents for Core. Install this agent at netowork node to enable ip redirections.
    """
    task_type = 'network'
    supported_actions = ['attach', 'detach', 'redirect', 'remove_redirection', 'prepare', 'delete']


    def __update_firewall(self, public_lease, redirections):
        chain = str('REDIR_' + public_lease.id)[:28]

        if len(redirections) > 0:
            system.call('sudo ip link add %s type dummy' % public_lease.redirection_ifname, shell=True)
            system.call('sudo ip addr add %s/%d dev %s' % (public_lease.address, 32, public_lease.redirection_ifname), shell=True)
            system.call(['sudo',
                             'iptables',
                             '-t', 'nat',
                             '-N',  chain])
            system.call(['sudo',
                             'iptables',
                             '-t', 'nat',
                             '-F', chain])
            system.call(['sudo',
                             'iptables',
                             '-t', 'nat',
                             '-D', 'CORE_REDIRECTION_DNAT',
                             '-d', public_lease.address,
                             '-j', chain])
            system.call(['sudo',
                             'iptables',
                             '-t', 'nat',
                             '-A', 'CORE_REDIRECTION_DNAT',
                             '-d', public_lease.address,
                             '-j', chain])

            i = float(len(redirections))
            for destination in redirections:
                system.call(['sudo',
                                 'iptables',
                                 '-t', 'nat',
                                 '-A', chain,
                                 '-p', 'tcp',
                                 '-m', 'state',
                                 '--state', 'NEW',
                                 '-m', 'statistic',
                                 '--mode', 'random',
                                 '--probability', str(1.0/i),
                                 '-j', 'DNAT',
                                 '--to-destination', destination.vm_address])
                i -= 1
        else:
            system.call('sudo ip link del %s' % public_lease.redirection_ifname, shell=True)
            system.call('sudo iptables -t nat -X ' + chain, shell=True)
            system.call('sudo iptables -t nat -D CORE_REDIRECTION_DNAT -d %s -j %s' % (public_lease.address, chain), shell=True)


    def prepare(self, task):
        '''
        Prepare network on network create. This may be used to create network namespace on CoreCluster machine (or agent host)
        '''
        network = task.get_obj('Subnet')
        if network.network_pool.mode == 'isolated':
            system.netns_add(network.netns_name)
            system.call(['sudo',
                         'ip',
                         'link',
                         'add',
                         network.isolated_port_name,
                         'type', 'vxlan',
                         'id', str(network.v_id),
                         'group', config.get('network', 'VXLAN_MULTICAST'),
                         'ttl', '4',
                         'dev', config.get('network', 'VXLAN_INTERFACE')])

            system.call(['sudo',
                         'ip',
                         'link',
                         'set',
                         network.isolated_port_name,
                         'up'])

            system.call(['sudo',
                         'ip',
                         'link',
                         'set',
                         network.isolated_port_name,
                         'netns',
                         network.netns_name])


            # Create veth pair and assign it's peer to proper network namespace
            system.call(['sudo', 'ip', 'link', 'add', network.isolated_veth_name, 'type', 'veth', 'peer', 'name', network.isolated_peer_name])
            system.call(['sudo', 'ip', 'link', 'set', network.isolated_peer_name, 'netns', network.netns_name])

            # Create bridge and connect it with interfaces
            system.call(['sudo', 'brctl', 'addbr', network.isolated_bridge_name])
            system.call(['sudo', 'brctl', 'addif', network.isolated_bridge_name, network.isolated_veth_name])

            # Create network internal bridge and add interfaces
            system.call(['brctl', 'addbr', network.isolated_bridge_name], netns=network.netns_name)
            system.call(['brctl', 'addif', network.isolated_bridge_name, network.isolated_port_name], netns=network.netns_name)
            system.call(['brctl', 'addif', network.isolated_bridge_name, network.isolated_peer_name], netns=network.netns_name)

            # Bring up all necessary interfaces
            system.call(['ip', 'link', 'set', network.isolated_peer_name, 'up'], netns=network.netns_name)
            system.call(['ip', 'link', 'set', network.isolated_bridge_name, 'up'], netns=network.netns_name)
            system.call(['ip', 'link', 'set', network.isolated_port_name, 'up'], netns=network.netns_name)
            system.call(['sudo', 'ip', 'link', 'set', network.isolated_veth_name, 'up'])
            system.call(['sudo', 'ip', 'link', 'set', network.isolated_bridge_name, 'up'])

        elif network.network_pool.mode == 'routed':
            #TODO: Open internet access for this network at this agent
            pass
        else:
            pass


    def delete(self, task):
        '''
        Remove network from agent host or CoreCluster. This is called on network delete.
        '''
        network = task.get_obj('Subnet')
        if network.network_pool.mode == 'isolated':
            # Shutdown all interfaces
            system.call(['ip', 'link', 'set', network.isolated_peer_name, 'down'], netns=network.netns_name)
            system.call(['ip', 'link', 'set', network.isolated_bridge_name, 'down'], netns=network.netns_name)
            system.call(['ip', 'link', 'set', network.isolated_port_name, 'down'], netns=network.netns_name)
            system.call(['sudo', 'ip', 'link', 'set', network.isolated_veth_name, 'down'])
            system.call(['sudo', 'ip', 'link', 'set', network.isolated_bridge_name, 'down'])


            # Remove bridges and peer
            system.call(['brctl', 'delbr', network.isolated_bridge_name], netns=network.netns_name)
            system.call(['sudo', 'brctl', 'delbr', network.isolated_bridge_name])
            system.call(['sudo', 'ip', 'link', 'del', network.isolated_veth_name])
            system.call(['ip', 'link', 'del', network.isolated_port_name], netns=network.netns_name)

            # Remove main interface conected to vlan
            system.call(['ip', 'link', 'del', network.isolated_peer_name], netns=network.netns_name)

            # Remove network ns
            system.netns_delete(network.netns_name)
        elif network.network_pool.mode == 'routed':
            #TODO: Close internet access for this network at this agent
            pass
        else:
            pass

        network.delete()


    def attach(self, task):
        '''
        Attach network to VM
        '''
        lease = task.get_obj('Lease')
        vm = task.get_obj('VM')

        vm.node.check_online(task.ignore_errors)

        if lease.subnet.network_pool.mode not in ("isolated", "routed"):
            raise TaskError('network_wrong_type')

        if not vm.in_state('stopped'):
            raise TaskError('network_vm_not_stopped')

        conn = vm.node.libvirt_conn()

        try:
            lease.vm = vm
            lease.save()
            network_xml = lease.libvirt_xml()

            if lease.subnet.is_isolated:
                firewall_xml = lease.firewall_xml()
                log(msg="Attaching firewall for vm %s with xml:\n%s" % (vm.id, firewall_xml), context=task.logger_ctx, tags=('agent', 'network', 'info'))
                fw = conn.nwfilterDefineXML(firewall_xml)


            log(msg="Attaching lease %s for vm %s with xml:\n%s" % (lease.id, vm.id, network_xml), context=task.logger_ctx, tags=('agent', 'network', 'info'))
            net = conn.networkDefineXML(network_xml)
            net.setAutostart(1)
            net.create()

        except Exception as e:
            conn.close()
            raise TaskError('network_create_failed', exception=e)

        # Create device xml for vm
        Device.create(lease.id, vm, 'devices/lease.xml', {'lease': lease})
        vm.libvirt_redefine()

        conn.close()


    def detach(self, task):
        '''
        Detach network from VM
        '''
        lease = task.get_obj('Lease')
        vm = task.get_obj('VM')

        vm.node.check_online(task.ignore_errors)

        if lease.subnet.network_pool.mode not in ("isolated", "routed"):
            raise TaskError('network_unsupported_type')

        conn = vm.node.libvirt_conn()

        lease.vm = None
        lease.save()

        try:
            fw = conn.nwfilterLookupByName(lease.vm_ifname)
            fw.undefine()
        except:
            log(msg="Firewall for vm %s not found" % vm.id, context=task.logger_ctx, tags=('agent', 'network', 'alert'))

        try:
            net = conn.networkLookupByName(lease.vm_ifname)
            net.destroy()
            net.undefine()
        except Exception as e:
            log(msg='Failed to find network', context=task.logger_ctx, tags=('agent', 'network', 'info'), exception=e)
            conn.close()
            raise TaskError('network_detach_failed', exception=e)

        for device in Device.objects.filter(object_id=lease.id).all():
            device.delete()

        try:
            vm.libvirt_redefine()
        except:
            pass

        conn.close()


    def redirect(self, task):
        '''
        Redirect public lease to private lease
        '''
        private_lease = Lease.objects.get(pk=task.get_prop('private_lease'))
        public_lease = Lease.objects.get(pk=task.get_prop('public_lease'))

        private_lease.redirected = public_lease
        private_lease.save()

        # if private_lease.vm == None:
        #     raise TaskError('network_private_lease_detached')

        # if public_lease.redirected != None:
        #     raise TaskError('network_lease_redirected')

        redirections = public_lease.redirected_set.all()
        self.__update_firewall(public_lease, redirections)


    def remove_redirection(self, task):
        '''
        Remove redirection from public lease to private lease
        '''
        public_lease = Lease.objects.get(pk=task.get_prop('public_lease'))
        private_lease = Lease.objects.get(pk=task.get_prop('private_lease'))

        if public_lease.subnet.network_pool.mode != "public":
            raise TaskError('network_unsupported_type')

        redirections = public_lease.redirected_set.all()
        self.__update_firewall(public_lease, redirections)

        private_lease.redirected = None
        private_lease.save()
