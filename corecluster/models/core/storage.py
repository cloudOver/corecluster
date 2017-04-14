# -*- coding: utf-8 -*-
# @COPYRIGHT_begin
#
# Copyright [2010-2014] Institute of Nuclear Physics PAN, Krakow, Poland
#           [2014-2015] Maciej Nabozny
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


import libvirt
from django.db import models
from django.db.models import Sum

from corecluster.utils.exception import CoreException
from corecluster.models.common_models import CoreModel, StateMixin
from corenetwork.utils.renderer import render


class Storage(StateMixin, CoreModel):
    states = [
        'ok',
        'locked',
        'disabled',
    ]

    default_state = 'locked'
    name = models.CharField(max_length=256)
    capacity = models.BigIntegerField(help_text="Total capacity in MB")
    address = models.GenericIPAddressField(null=True)
    dir = models.CharField(max_length=256, null=True)
    transport = models.CharField(max_length=20, default="netfs")

    serializable = ['id', 'data', 'name', 'capacity', 'state', 'address', 'dir', 'transport']


    def __unicode__(self):
        return self.name


    @property
    def path(self):
        """
        @returns{string} total mountpoint path to this Storage on the CM
        """
        try:
            conn = libvirt.open('qemu:///system')
            conn.storagePoolLookupByName(self.name)
        except:
            raise CoreException('storage_not_mounted')
        if self.transport == 'ssh':
            return self.dir
        else:
            return '/var/lib/cloudOver/storages/%s/' % self.name


    @property
    def used_space(self):
        """
        Returns space used by images in Megabytes
        """
        size = self.image_set.exclude(state='deleted').aggregate(Sum('size'))['size__sum']
        if size:
            return size/1024/1024
        else:
            return 0


    @property
    def free_space(self):
        """
        @returns{int} free space on this Storage [MB]
        """
        return self.capacity - self.used_space


    def lock(self):
        """
        Method sets this Storage's state as "locked".  Nothing can be read from
        or written to this Storage. Images saved on this Storage are displayed
        on the Web Interface as unavailable.
        """
        self.state = 'locked'


    def unlock(self):
        """
        Method sets this Storage's state as "ok". Storage may be used as usual.
        """
        self.state = 'ok'


    def libvirt_template(self):
        return render("pools/%s.xml" % self.transport, {'storage': self})
