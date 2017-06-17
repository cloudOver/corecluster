# -*- coding: utf-8 -*-
# @COPYRIGHT_begin
#
# Copyright [2010-2014] Institute of Nuclear Physics PAN, Krakow, Poland
#           [2015] Maciej Nabozny
#           [2015-2016] Marta Nabozny
#
# Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# @COPYRIGHT_end


import hashlib
import socket
import libvirt

from django.db import models
from django.db.models import Sum
from corecluster.utils.exception import CoreException
from corecluster.models.common_models import CoreModel, StateMixin
from corecluster.exceptions.agent import *
from corenetwork.utils.renderer import render
from corenetwork.utils.logger import log


class Node(StateMixin, CoreModel):
    """
    @model{NODE} Class for Nodes in the cluster

    Node is physical machine providing its CPU for virtual machines ran
    within cluster. It hosts VMs with help of underlying Libvirt software.
    CM automatically selects node fitting best for newly created VM.
    User doesn't know which node it is exacly. He doesn't even need to be
    aware of nodes existence.

    VMs may start only on node with 'ok' state. CM automatically disables
    starting VMs on failed nodes.
    """
    states = [
        'not registered',
        'not confirmed',
        'ok',
        'offline',
        'lock',
        'storage lock',
        'suspend',
        'waking up',
    ]

    default_state = 'not registered'

    username = models.CharField(max_length=30, help_text="User account which will be used to connect with this node")
    address = models.GenericIPAddressField(help_text="Node ip address")
    mac = models.CharField(max_length=30, help_text='Mac address for node wakeup', default='', blank=True)
    transport = models.CharField(max_length=45, default='ssh', help_text="Network transport for libvirt")
    driver = models.CharField(max_length=45, default='qemu', help_text="Virtualisation driver for libvirt. Used also as template name for VM definition")
    suffix = models.CharField(max_length=20, default='/system', help_text="Libvirt connection url suffix. /system for qemu")
    cpu_total = models.IntegerField(help_text="CPUs available for cloud")
    memory_total = models.IntegerField(help_text="Node's memory available for cloud in MB")
    hdd_total = models.IntegerField(help_text="Node's disk capacity in MB")
    comment = models.TextField(null=True, blank=True)
    auth_token = models.TextField(default='', null=True, blank=True, help_text="Authentication string used by this node to authenticate itself")

    serializable = ['id',
                    'username',
                    'address',
                    'transport',
                    'driver',
                    'suffix',
                    'cpu_total',
                    'memory_total',
                    'hdd_total',
                    'state',
    ]

    # method for printing object instance
    def __unicode__(self):
        return str(self.address)


    def libvirt_conn(self):
        """
        Get connection to libvirt
        """
        try:
            return libvirt.open('%s+%s://%s@%s%s' % (self.driver, self.transport, self.username, self.address, self.suffix))
        except Exception as e:
            log(msg='Cannot connect to node', exception=e, tags=('fatal', 'node', 'error', 'node:' + self.id))
            raise TaskError('node_connect', exception=e)


    @property
    def hostname(self):
        """
        Get node's auto-generated hostname for ospf
        """
        return 'node_' + self.id


    @property
    def router_id(self):
        """
        Get node's rotuer id for ospf
        """
        return self.address


    @property
    def cpu_free(self):
        """
        Calculate and return available cpu cores for this node
        """
        c = self.vm_set.exclude(state__in=['closed']).aggregate(cpu_sum=Sum('template__cpu'))
        csum = c['cpu_sum'] or 0  # 0 if no result exists in query

        c_free = self.cpu_total - csum

        return c_free


    @property
    def memory_free(self):
        """
        Calculate and return available memory for this node (in MB)
        """
        m = self.vm_set.exclude(state__in=['closed']).aggregate(memory_sum=Sum('template__memory'))
        msum = m['memory_sum'] or 0  # 0 if no results exists in query

        m_free = self.memory_total - msum

        return m_free


    @property
    def hdd_free(self):
        """
        Calculate and return available disk space at images pool (in MB)
        """
        s = self.vm_set.exclude(state__in=['closed']).exclude(base_image=None).aggregate(size_sum=Sum('base_image__size'))
        if s['size_sum']:
            return self.hdd_total - s['size_sum']/1024/1024
        else:
            return self.hdd_total



    @staticmethod
    def get(user_id, node_id):
        """
        @parameter{user_id,int} id of the declared Node's owner
        @parameter{node_id,int} requested Node's id

        @returns{Node} instance of the requested Node

        @raises{node_get,CoreException} no such Node
        """
        try:
            n = Node.objects.get(pk=node_id)
        except:
            raise CoreException('node_get')
        return n


    def check_online(self, ignore_errors=False):
        """
        Check if node is online. If not, raise TaskNotReady exception to delay task execution
        """
        if not self.in_state('ok') and not ignore_errors:
            raise TaskNotReady('node_offline')


    def check_auth(self, auth_hash, auth_seed):
        my_hash = hashlib.sha1(self.auth_token + auth_seed).hexdigest()
        if my_hash != auth_hash:
            raise CoreException('node_auth_failed')


    def images_pool_template(self, template='pools/images.xml'):
        return render(template, {'node': self})


    def start(self, storages=None):
        from corecluster.cache.task import Task
        from corecluster.models.core.storage import Storage

        self.set_state('offline')
        self.save()

        images = Task()
        images.node = self
        images.type = 'node'
        images.action = 'create_images_pool'
        images.append_to([self])

        if storages == None:
            for storage in Storage.objects.filter(state='ok'):
                task = Task()
                task.type = 'node'
                task.action = 'mount'
                task.append_to([self, storage])
        else:
            for storage in storages:
                task = Task()
                task.type = 'node'
                task.action = 'mount'
                task.append_to([storage, self])

        task = Task()
        task.type = 'node'
        task.action = 'check'
        task.append_to([self])


    def stop(self):
        from corecluster.cache.task import Task
        from corecluster.models.core.storage import Storage

        self.set_state('offline')
        self.save()

        for storage in Storage.objects.filter(state='ok'):
            task = Task()
            task.type = 'node'
            task.action = 'umount'
            task.append_to([self, storage])

