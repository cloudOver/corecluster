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


import datetime
from django.db import models
from corecluster.models.common_models import CoreModel


class Permission(CoreModel):
    """
    This model describes all API funcitons exposed with OverCluster/Core. It is used to
    control access to API for users, groups and particular tokens. It could be used to collect
    execution time statistics for all API calls (if DEBUG=True)
    """
    function = models.CharField(max_length=256)
    execution_time = models.DurationField(help_text="Total time spent on function execution. Divided by requests equals to average time", default=datetime.timedelta())
    requests = models.IntegerField(default=0)

    serializable = ['function']


    def __unicode__(self):
        return self.function


    @property
    def average_time(self):
        if self.requests > 0:
            return self.execution_time/self.requests
        else:
            return 0