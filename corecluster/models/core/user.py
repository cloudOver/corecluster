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


import hashlib
from netaddr import IPNetwork

from django.db import models
from django.db.models import Q
from django.db.models import Sum

from corecluster.utils.exception import CoreException
from corecluster.models.core.role import Role
from corecluster.models.core.group import Group
from corecluster.models.core.permission import Permission
from corecluster.models.common_models import CoreModel, StateMixin
from corenetwork.utils import config

class User(StateMixin, CoreModel):
    states = [
        'ok',
        'inactive',
        'inconfirmed',
        'removed',
    ]
    default_state = 'inactive'

    login = models.CharField(max_length=256)
    pw_hash = models.CharField(max_length=256)
    pw_seed = models.CharField(max_length=256)

    name = models.CharField(max_length=256)
    surname = models.CharField(max_length=256)
    email = models.CharField(max_length=256)

    group = models.ForeignKey(Group)
    role = models.ForeignKey(Role)

    registration_date = models.DateTimeField(auto_now_add=True)

    serializable = ['id',
                    'login',
                    'name',
                    'surname',
                    'email',
                    'group',
                    'role',
                    'registration_date',
                    'state']
    editable = ['name',
                'surname',
                'email']


    def __unicode__(self):
        return str(self.login)


    def make_pwd(self, password):
        self.pw_hash = 'sha512:' + hashlib.sha512(password + self.pw_seed).hexdigest()


    @staticmethod
    def create():
        # Create default role for all new users
        try:
            default_role = Role.objects.get(name='default_role')
        except:
            default_role = Role()
            default_role.name = 'default_role'
            default_role.description = 'Default role for new users'
            default_role.save()
            if config.get('core', 'ENABLE_ALL_PERMISSIONS'):
                default_role.permissions = Permission.objects.all()
                default_role.save()

        # Create additional groups for listing and storage only

        if config.get('core', 'CREATE_ADDITIONAL_ROLES'):
            try:
                ro_role = Role.objects.get(name='readonly_role')
            except:
                ro_role = Role()
                ro_role.name = 'readonly_role'
                ro_role.description = 'Read only role, for listing any items'
                ro_role.save()
                ro_role.permissions = Permission.objects.filter(Q(function__startswith='user/') | Q(function__startswith='api/api/') | Q(function__endswith='/get_list') | Q(function__endswith='/get_by_id') | Q(function__endswith='/get_list') | Q(function__contains='/image/get_')).all()
                ro_role.save()

            try:
                storage_role = Role.objects.get(name='storage_role')
            except:
                storage_role = Role()
                storage_role.name = 'storage_role'
                storage_role.description = 'Access to storage subsystem only'
                storage_role.save()
                storage_role.permissions = Permission.objects.filter(Q(function__startswith='user/') | Q(function__startswith='api/api/') | Q(function__startswith='api/storage') | Q(function__startswith='api/image')).all()
                storage_role.save()

            try:
                vm_role = Role.objects.get(name='readonly_role')
            except:
                vm_role = Role()
                vm_role.name = 'readonly_role'
                vm_role.description = 'Access to VM subsystem only'
                vm_role.function_filter = '^'
                vm_role.save()
                vm_role.permissions = Permission.objects.filter(Q(function__startswith='user/') | Q(function__startswith='api/api/') | Q(function__startswith='api/vm') | Q(function__contains='/image/get_') | Q(function__contains='/network/get_') | Q(function__contains='/network/attach')).all()
                vm_role.save()

        try:
            default_group = Group.objects.get(name='new_users')
        except:
            default_group = Group()
            default_group.name = 'new_users'
            default_group.description = 'Default group for new users'
            default_group.role = default_role
            default_group.quota_cpu = config.get('core', 'USER_QUOTA')['cpu']
            default_group.quota_memory = config.get('core', 'USER_QUOTA')['memory']
            default_group.quota_points = config.get('core', 'USER_QUOTA')['points']
            default_group.quota_redirections = config.get('core', 'USER_QUOTA')['redirections']
            default_group.quota_storage = config.get('core', 'USER_QUOTA')['storage']
            default_group.quota_lease_public = config.get('core', 'USER_QUOTA')['public_lease']
            default_group.quota_lease_routed = config.get('core', 'USER_QUOTA')['routed_lease']
            default_group.quota_network_isolated = config.get('core', 'USER_QUOTA')['network_isolated']
            default_group.save()

        u = User()
        u.group = default_group
        u.role = default_role
        u.state = 'inactive'
        return u


    @staticmethod
    def get_login(login, pw_hash):
        try:
            user = User.objects.get(login=login, pw_hash=pw_hash)
        except User.DoesNotExist:
            raise CoreException('user_not_found')

        if user.state != 'ok':
            raise CoreException('user_inactive')
        return user


    @staticmethod
    def get_token(token):
        from corecluster.models.core.token import Token
        try:
            t = Token.objects.get(token=token)
            return t.user
        except:
            raise CoreException('token_not_found')

    @property
    def total_vms(self):
        return self.vm_set.count()

    @property
    def defined_vms(self):
        return self.vm_set.exclude(state='closed').count()

    @property
    def running_vms(self):
        return self.vm_set.filter(state='running').count()

    def check_storage_quota(self, size):
        images_sum = 0
        for image in self.image_set.all():
            images_sum += image.size

        if images_sum+size > self.group.quota_storage:
            raise CoreException('storage_quota_exceeded')


    def check_quota(self, template):
        used_cpu = self.vm_set.exclude(state__in=('closed', 'failed')).aggregate(Sum('template__cpu'))['template__cpu__sum'] or 0
        if used_cpu + template.cpu > self.group.quota_cpu:
            raise CoreException('cpu_quota_exceeded')

        used_memory = self.vm_set.exclude(state__in=('closed', 'failed')).aggregate(Sum('template__memory'))['template__memory__sum'] or 0
        if used_memory + template.memory > self.group.quota_memory:
            raise CoreException('memory_quota_exceeded')


    def check_lease_quota(self, mode, requested_mask):
        leases = 0
        if mode == 'public':
            for subnet in self.subnet_set.filter(user=self).all():
                subnet.to_ipnetwork().size
            if leases + IPNetwork('0.0.0.0/%s' % requested_mask).size > self.group.quota_lease_public:
                raise CoreException('public_lease_quota_exceeded')
        elif mode == 'routed':
            for subnet in self.subnet_set.filter(user=self).all():
                subnet.to_ipnetwork().size / 4
            if leases + IPNetwork('0.0.0.0/%s' % requested_mask).size/4 > self.group.quota_lease_routed:
                raise CoreException('routed_lease_quota_exceeded')


    def check_network_quota(self, mode, requested):
        from corecluster.models.core.network_pool import NetworkPool

        if mode in ('isolated'):
            networks = 0
            for network in NetworkPool.objects.filter(mode=mode).all():
                networks += network.subnet_set.filter(user=self).count()

            if networks + requested > self.group.quota_network_isolated:
                raise CoreException('isolated_network_quota_exceeded')


    def get_quota(self):
        info = self.to_dict
        info['cpu_used'] = self.vm_set.exclude(state__in=['closed', 'failed']).aggregate(Sum('template__cpu'))['template__cpu__sum'] or 0
        info['cpu_quota'] = self.group.quota_cpu

        info['memory_used'] = self.vm_set.exclude(state__in=['closed', 'failed']).aggregate(Sum('template__memory'))['template__memory__sum'] or 0
        info['memory_quota'] = self.group.quota_memory

        info['storage_used'] = self.image_set.exclude(state__in=['deleted']).aggregate(Sum('size'))['size__sum'] or 0
        info['storage_quota'] = self.group.quota_storage

        public_lease_count = 0
        for subnet in self.subnet_set.filter(network_pool__mode='public').all():
            public_lease_count += subnet.to_ipnetwork().size
        info['public_lease_used'] = public_lease_count
        info['public_lease_quota'] = self.group.quota_lease_public

        routed_lease_count = 0
        for subnet in self.subnet_set.filter(network_pool__mode='routed').all():
            routed_lease_count += subnet.to_ipnetwork().size/4
        info['routed_lease_used'] = routed_lease_count
        info['routed_lease_quota'] = self.group.quota_lease_routed

        info['isolated_network_used'] = self.subnet_set.filter(network_pool__mode='isolated').count()
        info['isolated_network_quota'] = self.group.quota_network_isolated
        return info
