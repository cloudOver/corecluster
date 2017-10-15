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


import urllib

from corecluster.utils import validation as v
from corecluster.utils.decorators import register
from corecluster.utils.exception import CoreException
from corecluster.models.core.image import Image
from corecluster.models.core.vm import VM
from corecluster.cache.task import Task
from corecluster.cache.data_chunk import DataChunk
from corenetwork.utils import config
from corenetwork.utils.logger import log


@register(auth='token', log=True, validate={'name': v.is_string(),
                                            'description': v.is_string(empty=True),
                                            'size': v.is_integer(),
                                            'image_type': v.is_string(),
                                            'disk_controller': v.is_string(),
                                            'access': v.is_string(none=True),
                                            'format': v.is_string(none=True)})
def create(context, name, description, size, image_type, disk_controller=config.get('hardware', 'default_disk_controller'), access='private', format=config.get('hardware', 'default_image_format')):
    """ Create new image

    Args:
        name: image name
        description: image description
        size: image size in bytes
        image_type: type of image: transient, permanent, cd
        disk_controller: disk controller for this image (list available by get_disk_controllers)
        access: defines if image should be available only for owner, group or public
    Returns:
        New image description
    """
    context.user.check_storage_quota(size)

    image = Image.create(context.user, name, description, long(size), image_type, disk_controller, access, format)
    image.save()

    task = Task(user=context.user)
    task.type = 'image'
    task.state = 'not active'
    task.action = 'create'
    task.append_to([image, image.storage])

    return image.to_dict


@register(auth='token', log=True, validate={'image_id': v.is_id(),
                                            'url': v.is_string()})
def upload_url(context, image_id, url):
    """
    Upload data into given image from URL
    :param image_id: Id of image
    :param url: address with image's data
    :return: dictionary with image info
    """
    try:
        size = int(urllib.urlopen(url).info().getheaders('Content-Length')[0])
    except Exception as e:
        log(exception=e, msg='Cannot download image', context=context)
        raise CoreException('image_download')

    image = Image.get(context.user_id, image_id)

    task = Task(user=context.user)
    task.type = 'image'
    task.state = 'not active'
    task.action = 'upload_url'
    task.set_all_props({'offset': 0,
                        'size': size,
                        'url': url})
    task.append_to([image, image.storage])

    return image.to_dict


@register(auth='token', log=True, validate={'image_id': v.is_id(),
                                            'offset': v.is_integer(),
                                            'data': v.is_string()})
def upload_data(context, image_id, offset, data):
    """
    Upload chunk of data into image
    :param image_id: Id of the image
    :param offset: Data offset
    :param data: Data to be uploaded, encoded with base64
    :return: Dictionary with image
    """
    image = Image.get(context.user_id, image_id)

    if len(data) > config.get('core', 'MAX_UPLOAD_CHUNK_SIZE', 1024*1024*10):
        raise CoreException('image_data_too_large')

    chunk = DataChunk()
    chunk.data = data
    chunk.offset = offset
    chunk.image_id = image.id
    chunk.type = 'upload'
    chunk.save()

    task = Task(user=context.user)
    task.type = 'image'
    task.state = 'not active'
    task.action = 'upload_data'
    task.set_all_props({'offset': offset,
                        'size': len(data),
                        'chunk_id': chunk.cache_key()})

    task.append_to([image])

    return image.to_dict


@register(auth='token', validate={'type': v.is_string(none=True, empty=True),
                                  'access': v.is_string(none=True, empty=True),
                                  'prohibited_states': v.is_list(none=True, empty=True, is_tuple=True)})
def get_list(context, type=None, access=None, prohibited_states=['deleted']):
    """
    Get list of images
    :param type: Image types (transient, premanent, object)
    :param access: Image access
    :param prohibited_states: Which states should be filtered-out (by default deleted images are not listed)
    :return: List with images' dictionaries
    """
    criteria = {'access': access, 'type': type}
    if access is None or access == '':
        del criteria['access']
    if type is None or type == '':
        del criteria['type']

    if access is not None and access != '' and not access in Image.object_access:
        raise CoreException('image_unknown_access')

    if type is not None and type != '' and not type in Image.image_types:
        raise CoreException('image_unknown_type')

    images = Image.get_list(context.user_id, criteria=criteria, exclude={'state__in': prohibited_states}, order_by=['name'])

    return [img.to_dict for img in images]


@register(auth='token', validate={'image_id': v.is_id()})
def get_by_id(context, image_id):
    """ Get image with selected id

    Returns:
        Image description
    """
    return Image.get(context.user_id, image_id).to_dict


@register(auth='token', log=True, validate={'image_id': v.is_id()})
def delete(context, image_id):
    """ Delete image """
    image = Image.get(context.user_id, image_id)

    if image.user_id != context.user_id:
        raise CoreException('not_owner')

    if not image.in_states(['ok', 'failed']) and config.get('core', 'CHECK_STATES'):
        raise CoreException('image_wrong_state')

    if image.attached_to != None and config.get('core', 'CHECK_STATES', False):
        raise CoreException('image_attached')

    task = Task(user=context.user)
    task.type = 'image'
    task.state = 'not active'
    task.action = 'delete'
    task.append_to([image])


@register(auth='token')
def get_disk_controllers(context):
    """ Get list of disk controllers. Disk controller of image is used, when
    attaching disk to virtual machine.
    """
    return config.get('hardware', 'disk_controllers')


@register(auth='token')
def get_video_devices(context):
    """ Get list of video devices. Video device (driver) is used, when
    creating new virtual machine with given image as base_image
    """
    return config.get('hardware', 'video_devices')


@register(auth='token')
def get_network_devices(context):
    """ Get list of network devices. Network device (driver) is used, when
    creating new virtual machine with given image as base_image
    """
    return config.get('hardware', 'network_devices')


@register(auth='token')
def get_image_formats(context):
    """ Get list of network devices. Network device (driver) is used, when
    creating new virtual machine with given image as base_image
    """
    return config.get('hardware', 'image_formats')


@register(auth='token')
def get_image_types(context):
    """ Return all types of images """
    return Image.image_types


@register(auth='token', log=True, validate={'image_id': v.is_id(),
                                            'vm_id': v.is_id(),
                                            'device': v.is_integer(none=True)})
def attach(context, image_id, vm_id, device=None):
    """
    Attach image to VM as external disk
    :param image_id: An image to be attached
    :param vm_id: Instance, which should get new storage device
    :param device: device index (sda=1, sdb=2, ...), optional
    """
    image = Image.get(context.user_id, image_id)
    vm = VM.get(context.user_id, vm_id)

    if not vm.in_state('stopped') and config.get('core', 'CHECK_STATES', False):
        raise CoreException('vm_not_stopped')

    task = Task(user=context.user)
    task.type = 'image'
    task.state = 'not active'
    task.action = 'attach'
    if device is not None:
        task.set_prop('device', device)
    task.append_to([image, vm])


@register(auth='token', log=True, validate={'image_id': v.is_id(),
                                            'vm_id': v.is_id()})
def detach(context, image_id, vm_id):
    """ Detach image from VM """
    image = Image.get(context.user_id, image_id)
    vm = VM.get(context.user_id, vm_id)

    if not vm.in_state('stopped') and config.get('core', 'CHECK_STATES', False):
        raise CoreException('vm_not_stopped')

    task = Task(user=context.user)
    task.type = 'image'
    task.state = 'not active'
    task.action = 'detach'
    task.append_to([vm, image])


@register(auth='token', log=True, validate={'image_id': v.is_id()})
def edit(context, image_id, **kwargs):
    """ Edit VM properties """
    image = Image.get(context.user_id, image_id)
    image.edit(context, **kwargs)


@register(auth='token')
def describe(context):
    """ Show serializable and editable fields in model """
    return Image.describe_model()
