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

import datetime
import pwd
import os

from corecluster.utils.decorators import register as register_decorator
from corecluster.models.core.node import Node
from corecluster.models.core.agent import Agent
from corecluster.utils.exception import CoreException
from corenetwork.utils.logger import log
from corenetwork.utils import config


@register_decorator(auth='guest')
def register(context, auth_token, cpu_total, memory_total, hdd_total, username='cloudover', driver='qemu', transport='ssh', suffix='/system', mac=''):
    '''
    :param auth_token: Authorization token, which will be used to authenticate node in future
    :param cpu_total: Ammount of CPU shared by node with Cloud
    :param memory_total: Ammount of memory shared by node with Cloud
    :param hdd_total: Ammount of local disk space (usualy /images pool) shared with Cloud to host copies of transient images
    :param username: Username used to connect with node via ssh
    :param driver: Libvirt driver (default qemu)
    :param transport: Libvirt transport to node (default ssh)
    :param suffix: Libvirt suffix (/system for qemu driver)
    :return:
    '''
    try:
        node = Node.objects.get(auth_token=auth_token)
    except:
        if config.get('core', 'AUTOREGISTER_NODE', False):
            node = Node()
            node.address = context.remote_ip
            node.auth_token = auth_token
            node.username = username
            node.cpu_total = cpu_total
            node.memory_total = memory_total
            node.hdd_total = hdd_total
            node.driver = driver
            node.transport = transport
            node.suffix = suffix
            node.state = 'not confirmed'
            node.mac = mac
            node.save()
        else:
            raise CoreException('node_not_found')

    if node.auth_token is None or node.auth_token == '':
        node.auth_token = auth_token
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        node.comment = "%s\nNode (%s): Registering node" % (node.comment, date)
        node.save()
    else:
        raise CoreException('node_registered')


@register_decorator(auth='node')
def update_state(context, state, comment=""):
    log(msg="Changing state to " + state, context=context)

    if comment != "":
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context.node.comment = "%s\nNode (%s): %s" % (context.node.comment, date, comment)

    if context.node.state in ('lock', 'storage lock', 'not confirmed'):
        context.node.save()
        return

    if state == 'ok':
        context.node.start()
    elif state == 'offline':
        context.node.stop()
    else:
        context.node.state = state

    context.node.save()


@register_decorator(auth='node')
def get_quagga_token(context):
    return config.get('network', 'OSPF_TOKEN')


@register_decorator(auth='node')
def get_authorized_keys(context):
    keys = ''
    for agent in Agent.objects.filter(state='running'):
        keys = keys + agent.ssh_public_key + '\n'

    return {'keys': keys, 'user': context.node.username}
