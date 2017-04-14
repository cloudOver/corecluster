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
from corecluster.models.core.role import Role
from corecluster.models.common_models import CoreModel, UserMixin


class Group(CoreModel):
    name = models.CharField(max_length=45)
    description = models.TextField(default='')
    role = models.ForeignKey(Role)

    quota_memory = models.IntegerField(default=0)
    quota_cpu = models.IntegerField(default=0)
    quota_storage = models.BigIntegerField(help_text="Storage quota in bytes", default=0)
    quota_lease_routed = models.IntegerField(default=0)
    quota_lease_public = models.IntegerField(default=0)
    quota_network_isolated = models.IntegerField(default=0)
    quota_points = models.IntegerField(default=0)

    serializable = ['id', 'data', 'name', 'description', 'role'
                    'quota_memory',
                    'quota_cpu',
                    'quota_storage',
                    'quota_redirections',
                    'quota_points']

    def __unicode__(self):
        return self.name

