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


import corecluster.utils.validation as v
from corecluster.models.core.template import Template
from corecluster.models.core.image import Image
from corecluster.models.core.vm import VM
from corecluster.models.core import Device
from corecluster.cache.task import Task
from corecluster.utils.decorators import register
from corecluster.utils.exception import CoreException
from corenetwork.utils import config
import datetime

@register(auth='token', log=True, validate={'name': v.is_string(),
                                            'description': v.is_string(empty=True),
                                            'template_id': v.is_id(),
                                            'base_image_id': v.is_id(none=True)})
def create(context,
           name,
           description,
           template_id,
           base_image_id):
    """
    Create new virtual machine
    :param name: Name of instance
    :param description: Description
    :param template_id: Hardware template id
    :param base_image_id: Base image id (main storage with operating system). This image will be cloned for vm.
    :return:
    """

    template = Template.get(template_id)

    base_image = Image.get(context.user.id, base_image_id)
    if base_image.state != 'ok':
        raise CoreException('image_wrong_state')

    if base_image.type != 'transient':
        raise CoreException('image_wrong_type')


    if template.hdd < base_image.size/1024/1024:
        raise CoreException('template_hdd_quota')


    context.user.check_quota(template)

    vm = VM.create(name, description, base_image, template)
    vm.user_id = context.user_id
    vm.save()

    if base_image != None:
        Device.create(vm.base_image.id, vm, 'devices/base_image.xml', {'vm': vm})

        img = Task(user=context.user)
        img.user_id = context.user_id
        img.action = 'load_image'
        img.type = 'node'
        img.append_to([vm, vm.node, vm.base_image])

    Device.create(None, vm, 'devices/mouse.xml', {})
    Device.create(None, vm, 'devices/serial.xml', {})
    Device.create(None, vm, 'devices/random.xml', {})
    Device.create(None, vm, 'devices/video.xml', {'vm': vm})

    vm_create = Task(user=context.user)
    vm_create.user_id = context.user_id
    vm_create.action = 'create'
    vm_create.type = 'vm'
    vm_create.append_to([vm, vm.node])

    return vm.to_dict


@register(auth='token', log=True, validate={'vm_id': v.is_id()})
def start(context, vm_id):
    """ Start virtual machine
    """
    vm = VM.get(context.user_id, vm_id)
    if vm.state == 'saving':
        raise CoreException('vm_is_saving')

    if not vm.in_state('stopped') and config.get('core', 'CHECK_STATES', False):
        raise CoreException('vm_not_running')

    task = Task(user=context.user)
    task.action = 'start_vm'
    task.type = 'vm'
    task.append_to([vm, vm.node])


@register(auth='token', log=True, validate={'vm_id': v.is_id()})
def shutdown(context, vm_id):
    """ Send ACPI shutdown to virtual machine
    """
    vm = VM.get(context.user_id, vm_id)

    if not vm.in_state('running') and config.get('core', 'CHECK_STATES', False):
        raise CoreException('vm_not_running')

    task = Task(user=context.user)
    task.action = 'shutdown'
    task.type = 'vm'
    task.append_to([vm])


@register(auth='token', log=True, validate={'vm_id': v.is_id()})
def poweroff(context, vm_id):
    """ Power off virtual machine
    """
    vm = VM.get(context.user_id, vm_id)

    if not vm.in_state('running') and config.get('core', 'CHECK_STATES', False):
        raise CoreException('vm_not_running')

    task = Task(user=context.user)
    task.action = 'poweroff'
    task.type = 'vm'
    task.append_to([vm])


@register(auth='token', log=True, validate={'vm_id': v.is_id()})
def reset(context, vm_id):
    """ Reset virtual machine
    """
    vm = VM.get(context.user_id, vm_id)

    if not vm.in_state('running') and config.get('core', 'CHECK_STATES', False):
        raise CoreException('vm_not_running')

    task = Task(user=context.user)
    task.ignore_errors = True
    task.action = 'reset'
    task.type = 'vm'
    task.append_to([vm])


@register(auth='token', log=True, validate={'vm_id': v.is_id()})
def save_image(context, vm_id):
    """ Save image of virtual machine in stopped state
    """
    vm = VM.get(context.user_id, vm_id)
    if not vm.in_state('stopped'):
        raise CoreException('vm_not_stopped')

    if vm.base_image is None:
        raise CoreException('vm_has_no_base_image')

    image = Image.create(vm.user,
                         vm.name + '-save-' + str(datetime.datetime.now()),
                         vm.base_image.description,
                         vm.base_image.size,
                         vm.base_image.type,
                         vm.base_image.disk_controller,
                         'private',
                         vm.base_image.format)
    image.save()

    task = Task(user=context.user)
    task.action = 'save_image'
    task.type = 'node'
    task.append_to([vm, image, vm.node])


@register(auth='token', log=True, validate={'vm_id': v.is_id()})
def reload_image(context, vm_id):
    """
    Reload image to fresh copy of base_image
    """
    vm = VM.get(context.user_id, vm_id)

    task = Task(user=context.user)
    task.action = 'poweroff'
    task.type = 'vm'
    task.append_to([vm])

    task = Task(user=context.user)
    task.action = 'delete'
    task.type = 'node'
    task.append_to([vm, vm.node, vm.base_image])

    task = Task(user=context.user)
    task.action = 'load_image'
    task.type = 'node'
    task.append_to([vm, vm.node, vm.base_image])


@register(auth='token', log=True, validate={'vm_id': v.is_id()})
def cleanup(context, vm_id):
    """
    Remove all data connected with stopped virtual machine.
    """
    vm = VM.get(context.user_id, vm_id)

    if vm.user_id != context.user_id:
        raise CoreException('not_owner')

    vm.stop_time = datetime.datetime.now()
    vm.save()
    vm.cleanup()


@register(auth='token', log=True, validate={'vm_id': v.is_id()})
def console(context, vm_id, enable):
    """
    Enable or disable web console (novnc) for VM
    """
    vm = VM.get(context.user_id, vm_id)
    task = Task(user=context.user)
    task.type = 'console'
    if enable:
        task.action = 'attach_vnc'
    else:
        task.action = 'detach_vnc'

    task.append_to([vm])


@register(auth='token', log=True, validate={'vm_id': v.is_id()})
def resize(context, vm_id, size):
    """
    Resize base image of VM to given size. Use size='max' to set maximum size
    allowed by template
    """
    vm = VM.get(context.user_id, vm_id)

    if size == 'max':
        size = vm.template.hdd * 1024 * 1024

    if size > vm.template.hdd*1024*1024:
        raise CoreException('size_exceeds_template')

    if size <= 0:
        raise CoreException('size_not_positive')
    
    task = Task(user=context.user)
    task.type = 'node'
    task.action = 'resize_image'
    task.set_prop('size', size)
    task.append_to([vm])


@register(auth='token')
def get_list(context):
    vms = VM.get_list(context.user_id, exclude={'state': 'closed'}, order_by=['name'])
    return [vm.to_dict for vm in vms]


@register(auth='token', validate={'vm_id': v.is_id()})
def get_by_id(context, vm_id):
    vm = VM.get(context.user_id, vm_id)
    return vm.to_dict


@register(auth='token', log=True)
def edit(context, vm_id, **kwargs):
    """ Edit VM properties """
    vm = VM.get(context.user_id, vm_id)
    vm.edit(context, **kwargs)


@register(auth='token')
def describe(context):
    """ Show serializable and editable fields in model """
    return VM.describe_model()
