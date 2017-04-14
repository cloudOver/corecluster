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
from corecluster.models.core.network_pool import NetworkPool
from corecluster.models.core.subnet import Subnet

@register(auth='token', log=True, validate={'address': v.is_string(none=True, empty=True),
                                            'mask': v.is_integer(),
                                            'name': v.is_string(empty=True),
                                            'isolated': v.is_integer(is_boolean=True, none=True),
                                            'mode': v.in_list(NetworkPool.modes, none=True)})
def create(context, address, mask, name, mode, isolated=False):
    """
    Request new network
    :param address: network address or none
    :param mask: network mask
    :param name: network's name
    :param isolated: should network be isolated from any other traffic (including the Internet)
    :param mode: Type of network (routed - network is routed; isolated - vlan based or vpn; public - public ip set)
    :return: dictionary with new network
    """

    context.user.check_lease_quota(mode, mask)
    context.user.check_network_quota(mode, 1)

    if mask < 0 or mask >= 32:
        raise CoreException('network_invalid_mask')

    if mode == 'routed':
        net = Subnet.create_routed(context, None, mask, name, isolated)
    elif mode == 'public':
        net = Subnet.create_public(context, None, mask, name, isolated)
    elif mode == 'isolated':
        net = Subnet.create_isolated(context, address, mask, name)
    else:
        raise CoreException('network_mode_not_supported')

    net.prepare()
    return net.to_dict


@register(auth='token', log=True, validate={'network_id': v.is_id()})
def allocate(context, network_id):
    """
    Populate routed or public network with leases
    """
    network = Subnet.get(context.user_id, network_id)
    network.allocate()


@register(auth='token', log=True, validate={'network_id': v.is_id()})
def delete(context, network_id):
    """
    Remove network
    """
    subnet = Subnet.get(context.user_id, network_id)

    if subnet.is_in_use():
        raise CoreException('network_in_use')

    subnet.release()


@register(auth='token')
def get_pool_list(context):
    """
    List all network pools, which are allowed to create new network inside
    """
    network_pools = NetworkPool.get_list(context.user_id, criteria={'state': 'ok'})
    response = []
    for network in network_pools:
        response.append(network.to_dict)
    return response


@register(auth='token')
def get_list(context):
    """
    Get list of all user's networks
    """
    try:
        subnets = Subnet.get_list(context.user_id, order_by=['name'])
    except:
        raise CoreException('network_not_found')

    response = []
    for network in subnets:
        if network.network_pool.state == 'ok':
            response.append(network.to_dict)
    return response


@register(auth='token', validate={'network_id': v.is_id()})
def get_by_id(context, network_id):
    """
    Get network by id
    """
    return Subnet.get(context.user_id, network_id).to_dict


@register(auth='token', log=True, validate={'network_id': v.is_id()})
def edit(context, network_id, **kwargs):
    """ Edit network properties """
    net = Subnet.get(context.user_id, network_id)
    net.edit(context, **kwargs)


@register(auth='token')
def describe(context):
    """ Show serializable and editable fields in model """
    return Subnet.describe_model()
