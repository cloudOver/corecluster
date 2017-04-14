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
from corecluster.models.core.agent import Agent


class AgentStateFilter(admin.SimpleListFilter):
    title = 'Agent state'
    parameter_name = 'state'

    def lookups(self, request, model_admin):
        filters = []
        for k in Agent.states:
            filters.append((k, k))
        return filters

    def queryset(self, request, queryset):
        if self.value() != None:
            return queryset.filter(state=self.value())


class AgentAdmin(admin.ModelAdmin):
    actions = ['shutdown', 'cleanup']
    readonly_fields = ['id', 'pid', 'hostname', 'type', 'tasks_processed', 'tasks_failed', 'state']
    list_display = ['type', 'pid', 'hostname', 'state', 'tasks_processed', 'tasks_failed', 'tasks_done']


    def has_add_permission(self, request):
        return False

    def has_edit_permission(self, request):
        return False

    def shutdown(self, request, queryset):
        for agent in queryset.all():
            agent.set_state('stopping')
            agent.save()
            self.message_user(request, 'Shutting down agent %s' % agent.id)

    shutdown.short_description = 'Shutdown'

    def cleanup(self, request, queryset):
        for agent in Agent.objects.filter(state__in=('done', 'stopping')):
            agent.delete()
    cleanup.short_description = 'Remove done agents from database'

admin_site.register(Agent, AgentAdmin)
