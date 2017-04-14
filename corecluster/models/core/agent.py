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
from corecluster.models.common_models import CoreModel, StateMixin

class Agent(CoreModel, StateMixin):
    """
    Agent model is related to Agent thread started in cloud.
    """

    states = [
        'init',
        'running',
        'stopping',
        'done',
    ]

    default_state = 'init'

    type = models.CharField(max_length=30)
    pid = models.IntegerField()
    hostname = models.CharField(max_length=64)

    tasks_processed = models.IntegerField(default=0)
    tasks_failed = models.IntegerField(default=0)

    alive = models.DateTimeField(auto_now_add=True)

    ssh_public_key = models.CharField(max_length=1024, default='')


    def __str__(self):
        return self.hostname + '_' + str(self.pid)

    @property
    def tasks_done(self):
        return self.tasks_processed - self.tasks_failed