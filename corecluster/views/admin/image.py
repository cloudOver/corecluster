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
from django.db.models import Count
from corecluster.views.admin_site import admin_site
from corecluster.models.core.image import Image
from corecluster.models.core.storage import Storage
from corecluster.models.core.user import User
from corecluster.cache.task import Task


class ImageStateFilter(admin.SimpleListFilter):
    title = 'Image state'
    parameter_name = 'state'

    def lookups(self, request, model_admin):
        filters = []
        for k in Image.states:
            filters.append((k, k))
        return filters

    def queryset(self, request, queryset):
        if self.value() != None:
            return queryset.filter(state=self.value())


class ImageTypeFilter(admin.SimpleListFilter):
    title = 'Image type'
    parameter_name = 'type'

    def lookups(self, request, model_admin):
        filters = []
        for k in Image.image_types:
            filters.append((k, k))
        return filters

    def queryset(self, request, queryset):
        if self.value() != None:
            return queryset.filter(image_type=self.value())


class ImageAccessFilter(admin.SimpleListFilter):
    title = 'Image access'
    parameter_name = 'access'

    def lookups(self, request, model_admin):
        filters = []
        for k in Image.object_access:
            filters.append((k, k))
        return filters

    def queryset(self, request, queryset):
        if self.value() != None:
            return queryset.filter(access=self.value())


class ImageUserFilter(admin.SimpleListFilter):
    title = 'Owner'
    parameter_name = 'user_id'

    def lookups(self, request, model_admin):
        filters = []
        for user in User.objects.annotate(images=Count('image')).filter(images__gt=0).all():
            filters.append((user.id, user.name + ' ' + user.surname))
        return filters

    def queryset(self, request, queryset):
        if self.value() != None:
            return queryset.filter(user_id=self.value())


class ImageStorageFilter(admin.SimpleListFilter):
    title = 'Storage'
    parameter_name = 'user_id'

    def lookups(self, request, model_admin):
        filters = []
        for storage in Storage.objects.all():
            filters.append((storage.id, storage.name + ' (' + str(storage.image_set.count()) + ' images)'))
        return filters

    def queryset(self, request, queryset):
        if self.value() != None:
            return queryset.filter(storage_id=self.value())


class ImageAdmin(admin.ModelAdmin):
    actions = ['delete', 'cleanup']
    list_display = ['name', 'owner', 'size', 'type', 'state', 'storage']
    readonly_fields = ['id', 'state', 'last_task']
    list_filter = (ImageStorageFilter, ImageStateFilter, ImageTypeFilter, ImageAccessFilter, ImageUserFilter)
    ordering = ('creation_date',)


    def has_add_permission(self, request):
        return False


    def has_edit_permission(self, request):
        return False


    def owner(self, obj):
        return obj.user.name + ' ' + obj.user.surname + ' (' + str(obj) + ')'


    def delete(self, request, queryset):
        names = []
        for image in queryset.all():
            task = Task()
            task.type = 'image'
            task.state = 'not active'
            task.action = 'delete'
            task.ignore_errors = True
            task.append_to([image])

            names.append(image.name)
        self.message_user(request, 'Image(s) %s will be removed.' % ', '.join(names))
    delete.short_description = 'Delete'


    def cleanup(self, request, queryset):
        for image in Image.objects.filter(state='deleted').all():
            image.delete()
            self.message_user(request, 'Image %s is removed from database.' % image.id)
    cleanup.short_description = 'Cleanup database from deleted images'

admin_site.register(Image, ImageAdmin)
