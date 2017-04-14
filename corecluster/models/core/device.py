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
from corenetwork.utils.renderer import render
from corecluster.models.common_models import CoreModel


class Device(CoreModel):
    """
    Additional devices, which are attached to VM
    """
    xml = models.TextField()
    vm = models.ForeignKey('VM')

    object_id = models.CharField(max_length=64, null=True, blank=True)

    @staticmethod
    def create(object_id, vm, template, context):
        """
        Create rendered device object from context and template
        :param template: Path fil file with template
        :param context: Dictionary with context (objects to be used in template)
        """
        xml_template = render(template, context)

        device = Device()
        device.object_id = object_id
        device.xml = xml_template
        device.vm = vm
        device.save()
        return device