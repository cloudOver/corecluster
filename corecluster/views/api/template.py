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


from corecluster.models.core.template import Template
from corecluster.utils.exception import CoreException
from corecluster.utils.decorators import register
from corecluster.utils import validation as v


@register(auth='token')
def get_list(context):
    '''
    Get list of available templates
    '''

    return [template.to_dict for template in Template.get_list(criteria={'state': 'active'}, order_by=['cpu', 'memory'])]


@register(auth='token', validate={'template_id': v.is_id()})
def get_by_id(context, template_id):
    '''
    Get template by id
    '''

    return Template.get(template_id).to_dict



@register(auth='token')
def capabilities(context):
    '''
    Get capabilites for each template in this cloud
    '''
    from corecluster.models.core import Node

    t = {}
    for template in Template.objects.filter(state='active'):
        t[template.id] = 0
        for node in Node.objects.filter(state='ok'):
            available_cpu = int(node.cpu_free / template.cpu)
            available_memory = int(node.memory_free / template.memory)
            t[template.id] += max(available_cpu, available_memory)
    return t


@register(auth='token')
def describe(context):
    """ Show serializable and editable fields in model """
    return Template.describe_model()