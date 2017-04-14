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


from corecluster.agents.base_agent import BaseAgent
from corecluster.exceptions.agent import *
from corenetwork.utils.logger import *
from corenetwork.utils import system, config

class AgentThread(BaseAgent):
    """
    Networking agents for Core. Install this agent at netowork node to enable ip redirections.
    """
    task_type = 'console'
    supported_actions = ['attach_vnc', 'detach_vnc']


    def attach_vnc(self, task):
        vm = task.get_obj('VM')

        if vm.vnc_enabled == True:
            return
        cmd = ['sudo',
               'iptables',
               '-t', 'nat',
               '-I', 'CORE_VNC_DNAT',
               '-p', 'tcp',
               '--dport', str(vm.vnc_port),
               '-j', 'DNAT',
               '--to-destination', '%s:%d' % (vm.node.address, vm.vnc_port)]
        r = system.call(cmd)

        system.call(['sudo',
                     'iptables',
                     '-t', 'nat',
                     '-I', 'CORE_VNC_MASQ',
                     '-p', 'tcp',
                     '--dport', str(vm.vnc_port),
                     '-j', 'MASQUERADE'])

        if r != 0:
            raise TaskError('redirection_failed')

        vm.vnc_enabled = True
        vm.vnc_address = config.get('core', 'VNC_ADDRESS')
        vm.save()


    def detach_vnc(self, task):
        vm = task.get_obj('VM')

        if vm.vnc_enabled == False:
            return
        system.call(['sudo',
                         'iptables',
                         '-t', 'nat',
                         '-D', 'CORE_VNC_DNAT',
                         '-p', 'tcp',
                         '--dport', str(vm.vnc_port),
                         '-j', 'DNAT',
                         '--to-destination', '%s:%d' % (vm.node.address, vm.vnc_port)])
        system.call(['sudo',
                         'iptables',
                         '-t', 'nat',
                         '-D', 'CORE_VNC_MASQ',
                         '-p', 'tcp',
                         '--dport', str(vm.vnc_port),
                         '-j', 'MASQUERADE'])
        #if r != 0:
        #    raise TaskError('redirection_failed')

        vm.vnc_enabled = False
        vm.save()
