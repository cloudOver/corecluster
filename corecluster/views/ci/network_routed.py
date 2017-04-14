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

import django.conf
from django.template import Context, Template
from corecluster.utils.decorators import register
from corenetwork.utils import config
from corenetwork.utils.logger import log


@register(auth='node', log=True)
def get_ospfd_template(context, interfaces):
    """
    Return node's ospf configuration for quagga
    :param interfaces: List of network interfaces used for cloud communication at node
    :param networks: List of networks available at node
    :return:
    """
    try:
        django.conf.settings.configure()
    except:
        pass
    t = Template(open('/etc/corenetwork/drivers/quagga/ospfd.template.conf').read(1024*1024*16))
    tmpl = t.render(Context({'interfaces': interfaces,
                             'hostname': context.node.hostname,
                             'password': config.get('network', 'QUAGGA_PASSWORD'),
                             'ospf_token': config.get('network', 'OSPF_TOKEN'),
                             'router_id': context.node.address}))
    log(msg='Created ospf template: %s' % tmpl, context=context)
    return tmpl

@register(auth='node', log=True)
def get_zebra_template(context, interfaces):
    """
    Return node's ospf configuration for quagga
    :param interfaces: List of network interfaces used for cloud communication at node
    :param networks: List of networks available at node
    :return:
    """
    try:
        django.conf.settings.configure()
    except:
        pass
    t = Template(open('/etc/corenetwork/drivers/quagga/zebra.template.conf').read(1024*1024*16))
    tmpl = t.render(Context({'interfaces': interfaces,
                             'hostname': context.node.hostname,
                             'password': config.get('network', 'QUAGGA_PASSWORD'),
                             'ospf_token': config.get('network', 'OSPF_TOKEN'),
                             'router_id': context.node.address}))
    log(msg='Created zebra template: %s' % tmpl, context=context)
    return tmpl


@register(auth='node', log=True)
def get_daemons_template(context, interfaces):
    """
    Return node's ospf configuration for quagga
    :param interfaces: List of network interfaces used for cloud communication at node
    :param networks: List of networks available at node
    :return:
    """
    try:
        django.conf.settings.configure()
    except:
        pass

    t = Template(open('/etc/corenetwork/drivers/quagga/daemons.template.conf').read(1024*1024*16))
    tmpl = t.render(Context({'interfaces': interfaces,
                             'hostname': context.node.hostname,
                             'password': config.get('network', 'QUAGGA_PASSWORD'),
                             'ospf_token': config.get('network', 'OSPF_TOKEN'),
                             'router_id': context.node.address}))
    log(msg='Created daemons template: %s' % tmpl, context=context)
    return tmpl
