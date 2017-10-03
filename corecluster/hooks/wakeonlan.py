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


from corenetwork.network_mixin import NetworkMixin
from corenetwork.os_mixin import OsMixin
from corenetwork.api_mixin import ApiMixin
from corenetwork.hook_interface import HookInterface
from corenetwork.utils.logger import log
from corecluster.models.core.node import Node

class Hook(NetworkMixin, OsMixin, ApiMixin, HookInterface):
    task = None

    def cron(self, interval):
        arp_table = open('/proc/net/arp', 'r').readlines()
        for entry in arp_table:
            fields = entry.split()
            if len(fields) < 3:
                continue
            ip = fields[0]
            mac = fields[3]
            if mac == '00:00:00:00:00:00':
                continue

            try:
                node = Node.objects.get(address=ip)
                node.mac = mac
                node.save()
                log(msg="Updated node's mac: %s - %s" % (ip, mac), loglevel='debug')
            except:
                pass