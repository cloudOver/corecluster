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
from corecluster.models.core.subnet import Subnet
from corecluster.cache.task import Task
from corecluster.models.core.lease import Lease


@register(auth='token', log=True)
def create(context, public_lease_id, private_lease_id):
    """
    Redirect public lease to private lease. If public lease points to more than one private lease,
    the redirection could be used as load balancer.
    :param public_lease_id: Public lease id, which should be redirected into private
    :param private_lease_id: Private lease id, which is attached to VM
    :return: None
    """
    public_lease = Lease.get(context.user_id, public_lease_id)
    private_lease = Lease.get(context.user_id, private_lease_id)

    if public_lease.subnet.network_pool.mode != 'public':
        raise CoreException('lease_not_in_public_network')

    if public_lease.subnet.network_pool.state != 'ok':
        raise CoreException('network_not_available')

    l = Task(user=context.user)
    l.set_prop('private_lease', private_lease.id)
    l.set_prop('public_lease', public_lease.id)
    l.action = 'redirect'
    l.type = 'network'
    l.append_to([public_lease])


@register(auth='token', log=True)
def delete(context, public_lease_id, private_lease_id):
    """
    Detach public lease private lease.
    """
    public_lease = Lease.get(context.user_id, public_lease_id)
    private_lease = Lease.get(context.user_id, private_lease_id)
    if public_lease.subnet.network_pool.mode != 'public':
        raise CoreException('lease_not_in_public_network')

    l = Task(user=context.user)
    l.set_prop('private_lease', private_lease.id)
    l.set_prop('public_lease', public_lease.id)
    l.action = 'remove_redirection'
    l.type = 'network'
    l.append_to([public_lease])


@register(auth='token', log=True)
def get_list(context, public_lease_id):
    public_lease = Lease.get(context.user_id, public_lease_id)
    return [lease.to_dict for lease in public_lease.redirection_set.all()]


@register(auth='token')
def describe(context):
    """ Show serializable and editable fields in model """
    return Subnet.describe_model()
