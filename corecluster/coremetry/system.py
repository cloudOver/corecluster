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

import libvirt
from coremetry.utils import record


def _monitor_system(conn):
    hostname = conn.getHostname()
    for interface in conn.listInterfaces():
        rx = open('/sys/class/net/' + interface + '/statistics/rx_bytes')
        rx_bytes = int(rx.read(10240))
        rx.close()

        rx = open('/sys/class/net/' + interface + '/statistics/rx_packets')
        rx_packets = int(rx.read(10240))
        rx.close()

        tx = open('/sys/class/net/' + interface + '/statistics/tx_bytes')
        tx_bytes = int(tx.read(10240))
        tx.close()

        tx = open('/sys/class/net/' + interface + '/statistics/tx_packets')
        tx_packets = int(tx.read(10240))
        tx.close()

        record.store('system_net_' + interface + '_rx_bytes', hostname, rx_bytes)
        record.store('system_net_' + interface + '_rx_packets', hostname, rx_packets)
        record.store('system_net_' + interface + '_tx_bytes', hostname, tx_bytes)
        record.store('system_net_' + interface + '_tx_packets', hostname, tx_packets)

    mem_stats = conn.getMemoryStats(libvirt.VIR_NODE_MEMORY_STATS_ALL_CELLS)

    record.store('system_memory_available', hostname, mem_stats['total'] - mem_stats['buffers'] - mem_stats['cached'])
    record.store('system_memory_free', hostname, mem_stats['free'])
    record.store('system_memory_total', hostname, mem_stats['total'])


def monitor():
    conn = libvirt.open('qemu:///system')
    _monitor_system(conn)
    conn.close()
