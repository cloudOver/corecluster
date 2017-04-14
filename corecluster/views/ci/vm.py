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

from corecluster.utils.decorators import register
from corecluster.utils.exception import CoreException
from corecluster.models.core.vm import VM
from corenetwork.utils.logger import log

@register(auth='node')
def update_state(context, vm_name, state):
    """ Update VM state. Triggered by libvirt's hook on vm start/release/destroy """
    try:
        vm_id = vm_name[3:]
        vm = VM.objects.get(id=vm_id)
    except:
        log(msg="Unknown vm from hook: %s" % vm_name, context=context)
        raise CoreException('vm_not_found')


    if vm.node.address != context.node.address:
        raise CoreException('bad_node')

    if state == 'running' and vm.in_states(['stopped', 'starting']):
        vm.set_state('running')
        vm.save()
    elif state == 'stopped' and vm.in_state('running'):
        vm.set_state('stopped')
        vm.save()
    vm.save()

