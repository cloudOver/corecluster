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
from corecluster.models.common_models import CoreModel, UserMixin
import hashlib
import random

class Token(UserMixin, CoreModel):
    name = models.CharField(max_length=256, default='')
    token = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    valid_to = models.DateTimeField(null=True)
    permissions = models.ManyToManyField('Permission', symmetrical=False, blank=True)
    ignore_permissions = models.BooleanField(default=True)

    def _permissions(self):
        r = []
        for p in self.permissions.all():
            r.append(p.function)
        return r

    def _hash(self):
        seed = hashlib.sha1(str(random.random())).hexdigest()[:10]
        token_hash = hashlib.sha512(seed + self.token).hexdigest()
        return str(self.id) + '-' + 'sha512' + '-' + seed + '-' + token_hash

    serializable = ['id', 'data', 'name', ['token', '_hash'], 'creation_date', 'valid_to', 'ignore_permissions', ['permissions', '_permissions']]
    editable = ['name', 'valid_to']

    def __unicode__(self):
        return self.token

