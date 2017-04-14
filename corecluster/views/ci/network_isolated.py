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

from corecluster.utils.exception import CoreException
from corecluster.utils.decorators import register
from corecluster.models.core.lease import Lease
from corenetwork.utils.logger import log


@register(auth='node', log=True)
def get_tag(context, network_name):
    network_id = network_name.split('-')[1]
    log(msg="Get vxlan id for %s network" % network_id, context=context)
    lease = Lease.objects.get(id__startswith=network_id)
    log(msg="Got network %s!" % lease.subnet.id, context=context)
    
    if lease.subnet.network_pool.mode != 'isolated':
        raise CoreException('network_not_isolated')
    else:
        return lease.subnet.v_id


@register(auth='node', log=True)
def get_port_name(context, network_name):
    network_id = network_name.split('-')[1]
    log(msg="Get vxlan id for %s network" % network_id, context=context)
    lease = Lease.objects.get(id__startswith=network_id)
    log(msg="Got network %s!" % lease.subnet.id, context=context)
    
    if lease.subnet.network_pool.mode != 'isolated':
        raise CoreException('network_not_isolated')
    else:
        return lease.isolated_port_name
