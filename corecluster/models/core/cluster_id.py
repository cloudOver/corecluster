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
from corecluster.models.common_models import CoreModel, UserMixin, id_generator


class ClusterID(CoreModel):
    '''
    This class will be used for monitoring cluster by coremetric module
    '''

    installation_id = models.CharField(max_length=150, default=id_generator)

    @staticmethod
    def obtain_id():
        if len(ClusterID.objects.all()) == 0:
            cv = ClusterID()
            cv.save()
            return cv.installation_id
        else:
            return ClusterID.objects.first().installation_id