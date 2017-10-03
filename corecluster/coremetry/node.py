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

from corecluster.models.core import Node
import libvirt
from coremetry.utils import record


def _monitor_node(node, conn):
    mem_stats = conn.getMemoryStats(libvirt.VIR_NODE_MEMORY_STATS_ALL_CELLS)

    record.store('node_memory_available', node.id, mem_stats['total'] - mem_stats['buffers'] - mem_stats['cached'])
    record.store('node_memory_free', node.id, mem_stats['free'])
    record.store('node_memory_total', node.id, mem_stats['total'])

    arch, mem_total_mb, cpus, cpu_freq_mhz, numa_nodes, sockets_per_node, cores_per_socket, threads_per_core = conn.getInfo()

    idle = 0
    iowait = 0
    kernel = 0
    user = 0
    for core in xrange(numa_nodes * sockets_per_node * cores_per_socket * threads_per_core):
        cpu_stats = conn.getCPUStats(core)
        idle += cpu_stats['idle']
        iowait += cpu_stats['iowait']
        kernel += cpu_stats['kernel']
        user += cpu_stats['user']

    record.store('node_cpu_idle', node.id, idle)
    record.store('node_cpu_iowait', node.id, iowait)
    record.store('node_cpu_kernel', node.id, kernel)
    record.store('node_cpu_user', node.id, user)

    record.store('node_vms_defined', node.id, node.vm_set.count())
    record.store('node_vms_running', node.id, node.vm_set.filter(state='running').count())
    record.store('node_vms_real', node.id, len(conn.listDomainsID()))

    storage = conn.storagePoolLookupByName('images')
    storage.refresh()
    record.store('node_images_pool_allocated', node.id, storage.info()[2])
    record.store('node_images_pool_free', node.id, storage.info()[3])
    record.store('node_images_volumes_real', node.id, len(storage.listAllVolumes()))
    record.store('node_images_volumes_defined', node.id, node.vm_set.exclude(base_image=None).count())


def monitor():
    for node in Node.objects.filter(state='ok'):
        conn = node.libvirt_conn()
        _monitor_node(node, conn)
        conn.close()
