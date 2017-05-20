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
from corecluster.models.core.vm import VM
from corecluster.models.core.node import Node
from corecluster.models.core.user import User


class VMStateFilter(admin.SimpleListFilter):
    title = 'VM state'
    parameter_name = 'state'

    def lookups(self, request, model_admin):
        filters = []
        for k in VM.states:
            filters.append((k, k))
        return filters

    def queryset(self, request, queryset):
        if self.value() != None:
            return queryset.filter(state=self.value())


class VMNodeFilter(admin.SimpleListFilter):
    title = 'Node'
    parameter_name = 'node_id'

    def lookups(self, request, model_admin):
        filters = []
        for node in Node.objects.all():
            filters.append((node.id, node.address + '(' + str(node.vm_set.count()) + ')'))
        return filters

    def queryset(self, request, queryset):
        if self.value() != None:
            return queryset.filter(node_id=self.value())


class VMUserFilter(admin.SimpleListFilter):
    title = 'Owner'
    parameter_name = 'user_id'

    def lookups(self, request, model_admin):
        filters = []
        for user in User.objects.annotate(vms=Count('vm')).filter(vms__gt=0).all():
            filters.append((user.id, user.name + ' ' + user.surname))
        return filters

    def queryset(self, request, queryset):
        if self.value() != None:
            return queryset.filter(user_id=self.value())


class VMAdmin(admin.ModelAdmin):
    actions = ['delete', 'erase']
    list_display = ['name', 'owner', 'template_details', 'state', 'start_time', 'stop_time']
    list_filter = (VMStateFilter, VMNodeFilter)
    readonly_fields = ['id', 'state', 'last_task']
    ordering = ('start_time',)


    def has_add_permission(self, request):
        return False


    def has_edit_permission(self, request):
        return False


    def save_model(self, request, obj, form, change):
        obj.set_state(obj.default_state)
        obj.save()


    def erase(self, request, queryset):
        names = []
        for vm in queryset.all():
            vm.cleanup(True)
        self.message_user(request, 'VM(s) %s are marked to delete.' % ', '.join(names))
    erase.short_description = 'Force remove VM'


    def delete(self, request, queryset):
        names = []
        for vm in queryset.all():
            vm.cleanup(False)
        self.message_user(request, 'VM(s) %s are marked to delete.' % ', '.join(names))
    delete.short_description = 'Gently remove VM'


    def owner(self, obj):
        return obj.user.name + ' ' + obj.user.surname


    def template_details(self, obj):
        return str(obj.template) + ' (' + str(obj.template.cpu) + 'CPU ' + str(obj.template.memory) + 'MB Ram)'


admin_site.register(VM, VMAdmin)
