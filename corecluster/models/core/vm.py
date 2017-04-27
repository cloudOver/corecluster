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
import hashlib
import importlib
import libvirt
import random
import uuid

from netaddr import IPNetwork

from django.db import models

from corenetwork.utils.renderer import render
import corecluster.utils.validation as v
from corecluster.utils.exception import CoreException
from corecluster.exceptions.agent import *
from corecluster.models.common_models import CoreModel, UserMixin, StateMixin
from corenetwork.utils import config
from corenetwork.utils.logger import log


class VM(StateMixin, UserMixin, CoreModel):
    states = [
        'init',
        'stopped',
        'starting',
        'running',
        'reseting',
        'saving',
        'closing',
        'closed',
        'failed',
        'suspending',
        'suspended',
    ]
    default_state = 'init'

    name = models.CharField(max_length=128)
    description = models.TextField(default='')
    node = models.ForeignKey("Node")
    template = models.ForeignKey("Template")
    base_image = models.ForeignKey("Image", null=True)
    libvirt_id = models.IntegerField()
    start_time = models.DateTimeField(auto_now_add=True)
    stop_time = models.DateTimeField(null=True, blank=True)

    vnc_port = models.IntegerField()
    vnc_address = models.CharField(null=True, max_length=128, default='')
    vnc_enabled = models.BooleanField(default=False)
    vnc_passwd = models.CharField(null=True, max_length=50)
    save_on_destroy = models.BooleanField(default=False)

    serializable = ['id',
                    'data',
                    'name',
                    'description',
                    'template',
                    'base_image',
                    ['state', 'get_state'],
                    'start_time',
                    'stop_time',
                    'vnc_port',
                    'vnc_enabled',
                    'vnc_passwd',
                    'vnc_address',
                    'save_on_destroy',
                    'access',
                    ['tasks', 'get_tasks'],
                    ['disks', 'get_disks'],
                    ['leases', 'get_leases']]

    editable = [['name',        v.is_string()],
                ['description', v.is_string(empty=True, none=True)],
                ['access',      v.in_list(UserMixin.object_access)]]

    def __unicode__(self):
        return self.name


    def get_state(self):
        if 'locked' in [i.storage.state for i in self.image_set.all()]:
            return 'storage offline'
        elif self.node.state == 'ok':
            return self.state
        else:
            return 'node offline'


    def get_leases(self):
        leases = self.lease_set.all()
        if leases:
            return [l.to_dict for l in leases]
        else:
            return []


    def get_disks(self):
        disks = self.image_set.all()
        if disks:
            return [d.to_dict for d in disks]
        else:
            return []


    @staticmethod
    def create(name,
               description,
               base_image,
               template):
        '''
        Create new VM entity in database.
        :param name: Name of VM
        :param description:
        :param base_image:
        :param template:
        :return:
        '''
        vm = VM()
        vm.name = name
        vm.description = description
        vm.template = template
        vm.base_image = base_image
        vm.libvirt_id = -1
        vm.state = 'init'
        vm.start_time = datetime.datetime.now()

        vm.vnc_enabled = False
        vm.vnc_port = VM.get_vnc_port()
        vm.vnc_passwd = hashlib.sha1(str(random.random())).hexdigest()[:20]
        vm.save_on_destroy = False

        node_algorithm = config.get_algorithm('NODE_SELECT')
        vm.node = node_algorithm.select(template, base_image)

        return vm


    @staticmethod
    def get_vnc_port():
        vms = VM.objects.exclude(state='closed')
        ports = [vm.vnc_port for vm in vms]
        port = config.get('core', 'VNC_PORTS')['START']
        while port in ports or port in config.get('core', 'VNC_PORTS')['EXCLUDE']:
            port = port+1
        return port


    @property
    def libvirt_template(self):
        return render("hypervisors/%s.xml" % self.node.driver,
                      {'vm': self,
                       'uuid':    uuid.uuid1(),
                      })


    @property
    def libvirt_name(self):
        return "vm-%s" % self.id


    def libvirt_redefine(self):
        conn = self.node.libvirt_conn()

        try:
            dom = conn.lookupByName(self.libvirt_name)
            if dom.info()[0] != libvirt.VIR_DOMAIN_SHUTOFF:
                raise TaskError('vm_wrong_libvirt_state')
            dom.undefine()
            conn.defineXML(self.libvirt_template)
        except Exception as e:
            self.logger_ctx.vm = self
            self.logger_ctx.node = self.node
            log(context=self.logger_ctx, msg="Cannot redefine vm", exception=e, tags=('error'))
            raise TaskError('vm_redefine_failed', exception=e)

        conn.close()


    @staticmethod
    def get_by_ip(ip):
        ip = str(IPNetwork('%s/30' % ip).network)
        try:
            vm = VM.objects.filter(lease__address=ip)[0]
        except:
            raise CoreException('vm_get')

        return vm


    def cleanup(self, ignore_errors=False):
        from corecluster.cache.task import Task

        for task_id in self.get_prop('tasks', []):
            try:
                t = Task(cache_key=task_id)
                t.set_state('canceled')
                t.save()
            except:
                # Task not found
                pass

        self.stop_time = datetime.datetime.now()
        self.set_state('closing')
        self.save()

        task = Task()
        task.action = 'poweroff'
        task.type = 'vm'
        task.ignore_errors = ignore_errors
        task.append_to([self])

        for lease in self.lease_set.all():
            # Remove all public redirections
            from corecluster.models.core.lease import Lease
            for redirection in Lease.objects.filter(redirected=lease).all():
                l = Task()
                l.set_prop('public_lease', redirection.id)
                l.type = 'network'
                l.action = 'remove_redirection'
                l.ignore_errors = ignore_errors
                l.append_to([self, lease, redirection])

            # Detach leases
            d = Task()
            d.action = 'detach'
            d.type = 'network'
            d.ignore_errors = ignore_errors
            d.append_to([self, self.node, lease])

        # Detach all external disks
        for image in self.image_set.all():
            i = Task()
            i.action = 'detach'
            i.type = 'image'
            i.ignore_errors = ignore_errors
            i.append_to([self, image])

        if self.vnc_enabled:
            vnc_detach = Task()
            vnc_detach.type = 'console'
            vnc_detach.action = 'detach_vnc'
            vnc_detach.ignore_errors = ignore_errors
            vnc_detach.append_to([self])

        vm_delete = Task()
        vm_delete.action = 'delete'
        vm_delete.type = 'node'
        vm_delete.ignore_errors = ignore_errors
        vm_delete.append_to([self, self.node, self.base_image])

        vm_cleanup = Task()
        vm_cleanup.action = 'remove_vm'
        vm_cleanup.type = 'vm'
        vm_cleanup.ignore_errors = ignore_errors
        vm_cleanup.append_to([self, self.node])
