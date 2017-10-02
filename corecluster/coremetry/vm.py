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

from corecluster.models.core import Node, VM
from coremetry.utils import record
from xml.etree import ElementTree


def _monitor_vm(vm, conn):
    dom = conn.lookupByName(vm.libvirt_name)

    cpu_stats = dom.getCPUStats(True)
    record.store('vm_memory_used', vm.id, dom.memoryStats()['rss'], vm.user)
    record.store('vm_cpu_time', vm.id, cpu_stats['cpu_time'], vm.user)
    record.store('vm_system_time', vm.id, cpu_stats['system_time'], vm.user)
    record.store('vm_user_time', vm.id, cpu_stats['user_time'], vm.user)
    record.store('vm_cpu_time', vm.id, dom.info()[4], vm.user)

    tree = ElementTree.fromstring(dom.XMLDesc())
    for interface in tree.findall('devices/interface'):
        dev_name = interface.find('target').get('dev')
        dev_stats = dom.interfaceStats(dev_name)

        network_name = interface.find('source').get('network').split('-')[1]
        record.store('vm_net_in_bytes_' + network_name, vm.id, dev_stats[0], vm.user)
        record.store('vm_net_in_packets_' + network_name, vm.id, dev_stats[1], vm.user)
        record.store('vm_net_out_bytes_' + network_name, vm.id, dev_stats[4], vm.user)
        record.store('vm_net_out_packets_' + network_name, vm.id, dev_stats[5], vm.user)

    for disk in tree.findall('devices/disk'):
        dev_name = disk.find('target').get('dev')
        dev_stats = dom.blockStats(dev_name)

        record.store('vm_disk_read_bytes_' + dev_name, vm.id, dev_stats[1], vm.user)
        record.store('vm_disk_write_bytes_' + dev_name, vm.id, dev_stats[3], vm.user)


def monitor():
    for node in Node.objects.filter(state='ok'):
        conn = node.libvirt_conn()
        for vm in node.vm_set.filter(state='running'):
            record.monitor_vm(vm, conn)

        conn.close()
