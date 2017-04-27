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
def create(context, lease_id, port=80):
    """
    Create HTTP proxy to lease in routed network. If API is accessible over HTTPS, proxy is done with HTTPS, with the
    API's certificate.
    :param lease_id: Lease ID
    :return: None
    """
    lease = Lease.get(context.user_id, lease_id)
    if lease.subnet.network_pool.mode != 'routed':
        raise CoreException('least_not_in_routed_network')

    lease.proxy_enabled = True
    lease.proxy_port = port
    lease.save()


@register(auth='token', log=True)
def delete(context, lease_id):
    """
    Remove HTTP(s) proxy from lease
    """
    lease = Lease.get(context.user_id, lease_id)
    lease.proxy_enabled = False
    lease.save()


@register(auth='token')
def describe(context):
    """ Show serializable and editable fields in model """
    return Lease.describe_model()
