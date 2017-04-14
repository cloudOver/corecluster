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


from django.contrib import admin, messages
from corecluster.views.admin_site import admin_site
from corecluster.models.core.subnet import Subnet
from corecluster.models.core import NetworkPool


class SubnetPoolFilter(admin.SimpleListFilter):
    title = 'Network Pool'
    parameter_name = 'network_pool_id'

    def lookups(self, request, model_admin):
        filters = []
        for pool in NetworkPool.objects.all():
            filters.append((pool.id, pool.address + '(' + pool.mode + ', ' + str(pool.subnet_set.count()) + ' subnets)'))
        return filters

    def queryset(self, request, queryset):
        if self.value() != None:
            return queryset.filter(network_pool_id=self.value())


class SubnetAdmin(admin.ModelAdmin):
    actions = ['delete']
    readonly_fields = ['id', 'last_task']
    list_filter = (SubnetPoolFilter, )
    list_display = ['name', 'owner', 'address', 'mask', 'total_leases', 'attached_leases']


    def total_leases(self, obj):
        return len(obj.lease_set.all())


    def attached_leases(self, obj):
        return len(obj.lease_set.exclude(vm=None).all())


    def owner(self, obj):
        return obj.user.name + ' ' + obj.user.surname + ' (' + str(obj) + ')'


    def has_add_permission(self, request):
        return False


    def has_edit_permission(self, request):
        return False

    def delete(self, request, queryset):
        names = []
        for subnet in queryset.all():
            try:
                subnet.release()
                self.message_user(request, 'Subnet %s will be deleted' % subnet.address)
            except Exception as e:
                self.message_user(request, 'Failed to delete subnet %s: %s' % (subnet.address, str(e)), level=messages.ERROR)


    delete.short_description = 'Remove networks'


admin_site.register(Subnet, SubnetAdmin)
