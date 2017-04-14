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
from corecluster.utils import validation as v
from corecluster.models.core.subnet import Subnet
from corecluster.models.core.vm import VM
from corecluster.cache.task import Task
from corecluster.models.core.lease import Lease
from corenetwork.utils import config

from netaddr import IPAddress, IPNetwork


@register(auth='token', log=True, validate={'network_id': v.is_id(),
                                            'address': v.is_string()})
def create(context, network_id, address):
    """
    Create new lease in network
    :param network_id: Id of user network
    :param address: new ip address in network If network is inside 'routed' pool, then only 4n'th IPs are available, e.g.
    10.0.0.2; 10.0.0.6 and so on...
    :return: dictionary with lease description
    """
    subnet = Subnet.get(context.user_id, network_id)

    if not IPAddress(address) in subnet.to_ipnetwork():
        raise CoreException('lease_not_in_network')

    if Lease.objects.filter(subnet=subnet).filter(address=address).count() > 0:
        raise CoreException('lease_exists')

    if subnet.network_pool.mode in ['isolated', 'public']:
        lease = Lease()
        lease.address = address
        lease.subnet = subnet
        lease.user = subnet.user
        lease.save()
        return lease.to_dict
    elif subnet.network_pool.mode == 'routed':
        ip_subnet = IPNetwork('%s/30' % address)

        if ip_subnet.network+2 != IPAddress(address):
            raise CoreException('lease_not_available')

        lease = Lease()
        lease.address = str(ip_subnet.network)
        lease.subnet = subnet
        lease.user = subnet.user
        lease.save()
        return lease.to_dict
    else:
        raise CoreException('unsupported_network_mode')


@register(auth='token', log=True, validate={'lease_id': v.is_id()})
def delete(context, lease_id):
    """
    Remove network
    """
    lease = Lease.get(context.user_id, lease_id)

    if lease.vm != None and not lease.vm.in_state('closed'):
        raise CoreException('lease_in_use')

    lease.remove(context)

@register(auth='token', validate={'network_id': v.is_id(none=True)})
def get_list(context, network_id=None):
    """
    Get list of leases
    :param context:
    :param network_id: Optional parameter. List only networks from given subnet
    :return:
    """
    if network_id is None:
        return [l.to_dict for l in Lease.get_list(context.user_id)]
    else:
        return [l.to_dict for l in Lease.get_list(context.user_id, criteria={'subnet_id': network_id})]


@register(auth='token', validate={'network_id': v.is_id()})
def get_unused(context, network_id):
    """
    Get lease, which is not attached to any VM in given network.
    """
    network = Subnet.get(context.user_id, network_id)
    return network.get_unused().to_dict


@register(auth='token', validate={'lease_id': v.is_id()})
def get_by_id(context, lease_id):
    """
    Get lease by id
    """
    return Lease.get(context.user_id, lease_id).to_dict



@register(auth='token', log=True, validate={'lease_id': v.is_id(),
                                            'vm_id': v.is_id()})
def attach(context, lease_id, vm_id):
    """
    Attach lease to virtual machine
    :param lease_id: Lease id
    :param vm_id: Virtual machine id, which should get above lease
    :return: None
    """
    vm = VM.get(context.user_id, vm_id)
    lease = Lease.get(context.user_id, lease_id)

    if not vm.in_state('stopped') and config.get('core', 'CHECK_STATES', False):
        raise CoreException('vm_not_stopped')

    if lease.vm is not None and not lease.vm.in_state('closed'):
        raise CoreException('lease_attached')

    if lease.subnet.network_pool.mode == 'public':
        raise CoreException('network_pool_is_public')

    if lease.redirected is not None:
        raise CoreException('lease_redirected')

    if lease.subnet.network_pool.state != 'ok':
        raise CoreException('network_not_available')

    l = Task(user=context.user)
    l.action = 'attach'
    l.type = 'network'
    l.append_to([vm, vm.node, lease])


@register(auth='token', log=True, validate={'lease_id': v.is_id()})
def detach(context, lease_id):
    """
    Detach lease from vm. Could be executed only if lease is attached and
    machine is stopped
    :param lease_id: Lease id
    :return:
    """
    lease = Lease.get(context.user_id, lease_id)
    if lease.vm is None:
        raise CoreException('lease_detached')

    if not lease.vm.in_state('stopped') and config.get('core', 'CHECK_STATES', False):
        raise CoreException('vm_not_stopped')

    l = Task(user=context.user)
    l.action = 'detach'
    l.type = 'network'
    l.append_to([lease.vm, lease.vm.node, lease])


@register(auth='token')
def describe(context):
    """ Show serializable and editable fields in model """
    return Lease.describe_model()
