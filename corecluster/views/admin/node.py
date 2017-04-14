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
from corecluster.views.admin_site import admin_site
from corecluster.models.core.node import Node
from corecluster.cache.task import Task

class NodeStateFilter(admin.SimpleListFilter):
    title = 'Node state'
    parameter_name = 'state'

    def lookups(self, request, model_admin):
        filters = []
        for k in Node.states:
            filters.append((k, k))
        return filters

    def queryset(self, request, queryset):
        if self.value() != None:
            return queryset.filter(state=self.value())


class NodeAdmin(admin.ModelAdmin):
    actions = ['delete_selected', 'clear_log', 'reset_token', 'lock', 'enable', 'suspend', 'wake_up']
    list_display = ['address', 'running_vms', 'defined_vms', 'comment', 'state']
    readonly_fields = ['id', '_data', 'state', 'last_task']
    list_filter = (NodeStateFilter, )


    def save_model(self, request, obj, form, change):
        if obj.state is not None or obj.state != '':
            obj.set_state(obj.default_state)
            obj.save()


    def running_vms(self, obj):
        return len(obj.vm_set.filter(state='running').all())


    def defined_vms(self, obj):
        return len(obj.vm_set.exclude(state='closed').all())


    def clear_log(self, request, queryset):
        for n in queryset.all():
            n.comment = ''
            n.save()

        self.message_user(request, 'Log cleared')
    clear_log.short_description = 'Clear log'


    def reset_token(self, request, queryset):
        for n in queryset.all():
            n.auth_token = ''
            n.set_state(n.default_state)
            n.save()
    reset_token.short_description = 'Reset authentication token'


    def lock(self, request, queryset):
        for n in queryset.all():
            n.set_state('lock')
            n.save()
    lock.short_description = 'Lock'


    def enable(self, request, queryset):
        for n in queryset.all():
            n.state = 'offline'
            n.start()
            n.save()
    enable.short_description = 'Enable'


    def suspend(self, request, queryset):
        for n in queryset.all():
            t = Task()
            t.type = 'node'
            t.action = 'suspend'
            t.append_to([n])
    suspend.short_description = 'Suspend'


    def wake_up(self, request, queryset):
        for n in queryset.all():
            t = Task()
            t.type = 'node'
            t.action = 'wake_up'
            t.append_to([n])
    wake_up.short_description = 'Wake on Lan'

admin_site.register(Node, NodeAdmin)
