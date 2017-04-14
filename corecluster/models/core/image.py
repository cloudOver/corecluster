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


from django.db import models

from corecluster.models.core.storage import Storage
from corecluster.models.core.token import Token
from corecluster.models.common_models import UserMixin, CoreModel, StateMixin
from corecluster.utils.exception import CoreException
import corecluster.utils.validation as v
from corenetwork.utils.renderer import render
from corenetwork.utils import config

class Image(StateMixin, UserMixin, CoreModel):
    states = [
        'ok',
        'waiting',
        'unavailable',
        'failed',
        'deleted',
        'downloading',
    ]

    default_state = 'waiting'

    image_types = [
        'transient',  # VM Base images in qcow2 format
        'permanent',  # External drives, attached to VM dynamicly, in qcow2 format
        'cd',         # CD images in iso formats
        'object',     # Any other objects. Additional data could be stored in data field
    ]


    name = models.CharField(max_length=45)
    type = models.CharField(default='object', max_length=20, choices=[(k, k) for k in image_types])
    description = models.TextField()
    token = models.ForeignKey(Token, null=True, blank=True)
    
    attached_to = models.ForeignKey('VM', null=True, blank=True)

    video_device = models.CharField(max_length=10, default=config.get('hardware', 'default_video_device'), choices=[(k, k) for k in config.get('hardware', 'video_devices')])
    network_device= models.CharField(max_length=10, default=config.get('hardware', 'default_network_device'), choices=[(k, k) for k in config.get('hardware', 'network_devices')])
    disk_controller = models.CharField(max_length=10, default=config.get('hardware', 'default_disk_controller'), choices=[(k, k) for k in config.get('hardware', 'disk_controllers')])
    disk_dev = models.IntegerField(null=True, blank=True)

    creation_date = models.DateTimeField(auto_now_add=True)
    size = models.BigIntegerField(null=True, blank=True, help_text="Image file size in bytes")
    format = models.CharField(max_length=10, default=config.get('hardware', 'default_image_format'), choices=[(k, k) for k in config.get('hardware', 'image_formats')])
    storage = models.ForeignKey(Storage, null=True, blank=True)


    def __unicode__(self):
        return self.name


    serializable = ['id',
                    'data',
                    'name',
                    'description',
                    'disk_dev',
                    'creation_date',
                    'size',
                    'type',
                    'video_device',
                    'network_device',
                    'disk_controller',
                    'format',
                    'access',
                    ['state', 'get_state'],
                    ['tasks', 'get_tasks'],
                    'attached_to_id',
    ]

    editable = [['name',            v.is_string(empty=False)],
                ['description',     v.is_string(empty=True, none=True)],
                ['type',            v.in_list(values=['transient', 'permanent', 'cd', 'object'])],
                ['disk_controller', v.in_list(config.get('hardware', 'disk_controllers'))],
                ['video_device',    v.in_list(config.get('hardware', 'video_devices'))],
                ['network_device',  v.in_list(config.get('hardware', 'network_devices'))],
                ['access',          v.in_list(UserMixin.object_access)],
    ]

    def get_state(self):
        if self.storage.state == 'ok':
            return self.state
        else:
            return 'storage offline'


    @staticmethod
    def create(user, name, description, size, type, disk_controller, access, format):
        if format not in config.get('hardware', 'image_formats'):
            raise CoreException('image_format_not_supported')

        if disk_controller not in config.get('hardware', 'disk_controllers'):
            raise CoreException('disk_controller_not_supported')

        if access not in UserMixin.object_access:
            raise CoreException('access_not_supported')

        if type not in Image.image_types:
            raise CoreException('image_type_not_supported')

        image = Image()
        image.user = user
        image.disk_dev = 0
        image.size = size
        image.format = format

        storage_algorithm = config.get_algorithm('STORAGE_SELECT')
        image.storage = storage_algorithm.select(size)

        image.edit(name=name, description=description, type=type, access=access, disk_controller=disk_controller)

        return image


    def libvirt_xml(self):
        return render('volumes/image.xml', {
            'user': self.user,
            'image': self,
            'type': self.storage.transport,
        })


    @property
    def libvirt_name(self):
        return "%s_%s" % (self.user.id, self.id)


    @property
    def path(self):
        return self.storage.path + self.libvirt_name


    @property
    def disk_device(self):
        return 'sd' + chr(ord('a') + self.disk_dev)
