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
from corecluster.utils.exception import CoreException
from corecluster.models.common_models import CoreModel, StateMixin

class Template(StateMixin, CoreModel):
    states = [
        'active',
        'deleted',
    ]
    default_state = 'active'

    name = models.CharField(max_length=45)
    description = models.CharField(max_length=512)
    memory = models.IntegerField(help_text="Memory in megabytes")
    cpu = models.IntegerField()
    hdd = models.IntegerField(help_text="Maximum base image size in megabytes")
    points = models.IntegerField()
    ec2name = models.CharField(max_length=40, default='t1.micro', help_text="Amazon EC2 template equivalent")

    domain_type = models.CharField(max_length=64, default='hvm')
    kernel = models.CharField(max_length=256, default='', blank=True, null=True, help_text="Path to kernel used for booting virtual machine. If using default hvm type, leave it blank")
    initrd = models.CharField(max_length=256, default='', blank=True, null=True, help_text="Path to initrd used for booting virtual machine. If using default hvm type, leave it blank")
    cmdline = models.CharField(max_length=256, default='', blank=True, null=True, help_text="Kernel command line parameters. If using default hvm type, leave it blank")

    serializable = ['id', 'name', 'description', 'hdd', 'memory', 'cpu', 'state', 'points', 'ec2name', 'domain_type', 'kernel', 'initrd', 'cmdline']


    def __unicode__(self):
        return self.name


    @staticmethod
    def get(template_id):
        try:
            return Template.objects.filter(state='active').get(pk=template_id)
        except:
            raise CoreException('template_not_found')
