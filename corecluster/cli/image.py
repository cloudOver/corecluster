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

from corenetwork.cli.cli_base import CommandLineBase
from corecluster.models.core.image import Image
from corecluster.cache.task import Task

class Cmd(CommandLineBase):
    actions = {
        'list': {
            'help': 'List images',
        },
        'delete': {
            'help': 'Delete image'
        },
    }

    def list(self):
        print "ID\t\t\t\t\tState\tStorage\tName"
        for image in Image.objects.exclude(state='deleted'):
            print "%s\t%s\t%s\t%s" % (image.id, image.state, image.storage.name, image.name)

    def delete(self, id):
        image = Image.objects.get(pk=id)
        t = Task()
        t.type = 'image'
        t.action = 'delete'
        t.ignore_errors = True
        t.append_to([image, image.storage])
