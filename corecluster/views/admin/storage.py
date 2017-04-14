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


from django.contrib import admin
from django.db.models import Q

from corecluster.views.admin_site import admin_site
from corecluster.models.core.storage import Storage
from corecluster.cache.task import Task
from corecluster.models.core.node import Node


class StorageAdmin(admin.ModelAdmin):
    list_display = ['name', 'transport', 'address', 'dir', 'capacity', 'state', 'used_space']
    actions = ['mount_all', 'umount', 'disable']
    readonly_fields = ['id', '_data', 'state', 'last_task']


    def save_model(self, request, obj, form, change):
        obj.set_state(obj.default_state)
        obj.save()


    def mount_core(self, request, queryset):
        names = []
        for s in queryset.all():
            s.set_state('locked')
            s.save()

            mnt = Task()
            mnt.type = 'storage'
            mnt.action = 'mount'
            mnt.state = 'not active'
            mnt.append_to([s])

            names.append(s.name)
        self.message_user(request, 'Storage(s) %s are marked to mount. Should became available when mount is done.' % ', '.join(names))
    mount_core.short_description = 'Mount storage at core'


    def mount_nodes(self, request, queryset):
        for node in Node.objects.filter(state='ok'):
            node.set_state('offline')
            node.save()

        for node in Node.objects.filter(Q(state='ok') | Q(state='offline')):
            node.start(queryset)

        self.message_user(request, 'Storage(s) are marked to mount')
    mount_nodes.short_description = 'Mount storage on nodes'


    def mount_all(self, request, queryset):
        for node in Node.objects.filter(state='ok'):
            node.state = 'offline'
            node.save()

        self.mount_core(request, queryset)
        self.mount_nodes(request, queryset)
    mount_all.short_description = 'Mount and unlock'


    def umount(self, request, queryset):
        names = []
        for s in queryset.all():
            s.state = 'locked'
            s.save()

            umnt = Task()
            umnt.type = 'storage'
            umnt.storage = s
            umnt.action = 'umount'
            umnt.state = 'not active'
            umnt.append_to([s])

            names.append(s.name)
        self.message_user(request, 'Storage(s) %s are marked to mount. Should became available when mount is done.' % ', '.join(names))
    umount.short_description = 'Umount'

    def disable(self, request, queryset):
        names = []
        for s in queryset.all():
            s.state = 'disabled'
            s.save()

            names.append(s.name)
        self.message_user(request, 'Storage(s) %s are disabled.' % ', '.join(names))
    disable.short_description = 'Lock'


admin_site.register(Storage, StorageAdmin)
