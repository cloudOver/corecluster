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
from corecluster.utils.decorators import register
from corecluster.utils.exception import CoreException
from corecluster.cache.task import Task
from corenetwork.utils import config
import time


@register(auth='token', log=True)
def get_list(context):
    '''
    This function is no longer supported. It will be removed in 16.06
    '''
    return []


@register(auth='token', log=True, validate={'task_id': v.is_id()})
def cancel(context, task_id):
    """
    Cancel tasks by id
    """
    task = Task(cache_id=task_id)
    if task.user_id == context.user_id:
        task.set_state('canceled')
        task.save()


@register(auth='token', log=True, validate={'task_id': v.is_id()})
def wait(context, task_id, state, timeout=1000):
    '''
    Wail for task is done
    :param context:
    :param task_id:
    :param state:
    :param timeout:
    :return:
    '''
    for i in xrange(int(timeout/config.get('agent', 'TASK_FETCH_INTERVAL', 20))):
        task = Task(cache_key=task_id)

        if not hasattr(task, 'user_id') or task.user_id != context.user_id:
            raise CoreException('not_owner')

        if task.state == state:
            return
        else:
            time.sleep(config.get('agent', 'TASK_FETCH_INTERVAL', 20))
    raise CoreException('timeout')


@register(auth='token')
def describe(context):
    """ Show serializable and editable fields in model """
    return Task.describe_model()

