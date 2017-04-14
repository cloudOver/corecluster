# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import corecluster.models.common_models


class Migration(migrations.Migration):

    dependencies = [
        ('corecluster', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('_data', models.TextField(default=b'{}', help_text=b'Additional data. Leave blank if not used')),
                ('id', models.CharField(default=corecluster.models.common_models.id_generator, max_length=36, serialize=False, primary_key=True, help_text=b'API id used to identify all objects in Core')),
                ('xml', models.TextField()),
                ('object_id', models.CharField(max_length=64, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('_data', models.TextField(default=b'{}', help_text=b'Additional data. Leave blank if not used')),
                ('id', models.CharField(default=corecluster.models.common_models.id_generator, max_length=36, serialize=False, primary_key=True, help_text=b'API id used to identify all objects in Core')),
                ('name', models.CharField(max_length=45)),
                ('description', models.TextField(default=b'')),
                ('quota_memory', models.IntegerField(default=0)),
                ('quota_cpu', models.IntegerField(default=0)),
                ('quota_storage', models.BigIntegerField(default=0, help_text=b'Storage quota in bytes')),
                ('quota_redirections', models.IntegerField(default=0)),
                ('quota_points', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('_data', models.TextField(default=b'{}', help_text=b'Additional data. Leave blank if not used')),
                ('id', models.CharField(default=corecluster.models.common_models.id_generator, max_length=36, serialize=False, primary_key=True, help_text=b'API id used to identify all objects in Core')),
                ('access', models.CharField(default=b'private', max_length=30, choices=[(b'private', b'private'), (b'public', b'public'), (b'group', b'group')])),
                ('state', models.CharField(max_length=30)),
                ('name', models.CharField(max_length=45)),
                ('type', models.CharField(default=b'object', max_length=20, choices=[(b'transient', b'transient'), (b'permanent', b'permanent'), (b'cd', b'cd'), (b'object', b'object')])),
                ('description', models.TextField()),
                ('video_device', models.CharField(default=b'cirrus', max_length=10, choices=[(b'vga', b'vga'), (b'cirrus', b'cirrus'), (b'vmvga', b'vmvga'), (b'xen', b'xen'), (b'vbox', b'vbox'), (b'qxl', b'qxl')])),
                ('network_device', models.CharField(default=b'virtio', max_length=10, choices=[(b'virtio', b'virtio'), (b'ne2k_isa', b'ne2k_isa'), (b'i82551', b'i82551'), (b'i82557b', b'i82557b'), (b'i82559er', b'i82559er'), (b'ne2k_pci', b'ne2k_pci'), (b'pcnet', b'pcnet'), (b'rtl8139', b'rtl8139'), (b'e1000', b'e1000')])),
                ('disk_controller', models.CharField(default=b'ide', max_length=10, choices=[(b'virtio', b'virtio'), (b'scsi', b'scsi'), (b'sata', b'sata'), (b'ide', b'ide')])),
                ('disk_dev', models.IntegerField(null=True, blank=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('size', models.BigIntegerField(help_text=b'Image file size in bytes', null=True, blank=True)),
                ('format', models.CharField(default=b'qcow2', max_length=10, choices=[(b'qcow2', b'qcow2'), (b'raw', b'raw'), (b'qcow', b'qcow'), (b'vdi', b'vdi')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Lease',
            fields=[
                ('_data', models.TextField(default=b'{}', help_text=b'Additional data. Leave blank if not used')),
                ('id', models.CharField(default=corecluster.models.common_models.id_generator, max_length=36, serialize=False, primary_key=True, help_text=b'API id used to identify all objects in Core')),
                ('access', models.CharField(default=b'private', max_length=30, choices=[(b'private', b'private'), (b'public', b'public'), (b'group', b'group')])),
                ('address', models.CharField(max_length=20)),
                ('group', models.ForeignKey(blank=True, to='corecluster.Group', null=True)),
                ('redirected', models.ForeignKey(to='corecluster.Lease', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('_data', models.TextField(default=b'{}', help_text=b'Additional data. Leave blank if not used')),
                ('id', models.CharField(default=corecluster.models.common_models.id_generator, max_length=36, serialize=False, primary_key=True, help_text=b'API id used to identify all objects in Core')),
                ('state', models.CharField(max_length=30)),
                ('username', models.CharField(help_text=b'User account which will be used to connect with this node', max_length=30)),
                ('address', models.CharField(help_text=b'Router ip address', max_length=45)),
                ('transport', models.CharField(default=b'ssh', help_text=b'Network transport for libvirt', max_length=45)),
                ('driver', models.CharField(default=b'qemu', help_text=b'Virtualisation driver for libvirt. Used also as template name for VM definition', max_length=45)),
                ('suffix', models.CharField(default=b'/system', help_text=b'Libvirt connection url suffix. /system for qemu', max_length=20)),
                ('cpu_total', models.IntegerField(help_text=b'CPUs available for cloud')),
                ('memory_total', models.IntegerField(help_text=b"Node's memory available for cloud in MB")),
                ('hdd_total', models.IntegerField(help_text=b"Node's disk capacity in MB")),
                ('comment', models.TextField(null=True, blank=True)),
                ('auth_token', models.TextField(default=b'', help_text=b'Authentication string used by this node to authenticate itself', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('_data', models.TextField(default=b'{}', help_text=b'Additional data. Leave blank if not used')),
                ('id', models.CharField(default=corecluster.models.common_models.id_generator, max_length=36, serialize=False, primary_key=True, help_text=b'API id used to identify all objects in Core')),
                ('function', models.CharField(max_length=256)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('_data', models.TextField(default=b'{}', help_text=b'Additional data. Leave blank if not used')),
                ('id', models.CharField(default=corecluster.models.common_models.id_generator, max_length=36, serialize=False, primary_key=True, help_text=b'API id used to identify all objects in Core')),
                ('name', models.CharField(max_length=45)),
                ('description', models.TextField(default=b'')),
                ('permissions', models.ManyToManyField(to='corecluster.Permission', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('_data', models.TextField(default=b'{}', help_text=b'Additional data. Leave blank if not used')),
                ('id', models.CharField(default=corecluster.models.common_models.id_generator, max_length=36, serialize=False, primary_key=True, help_text=b'API id used to identify all objects in Core')),
                ('state', models.CharField(max_length=30)),
                ('name', models.CharField(max_length=256)),
                ('capacity', models.BigIntegerField(help_text=b'Total capacity in MB')),
                ('address', models.CharField(max_length=64, null=True)),
                ('dir', models.CharField(max_length=256, null=True)),
                ('transport', models.CharField(default=b'netfs', max_length=20)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('creation_time', models.DateTimeField(auto_now_add=True, auto_created=True)),
                ('_data', models.TextField(default=b'{}', help_text=b'Additional data. Leave blank if not used')),
                ('id', models.CharField(default=corecluster.models.common_models.id_generator, max_length=36, serialize=False, primary_key=True, help_text=b'API id used to identify all objects in Core')),
                ('state', models.CharField(max_length=30)),
                ('type', models.TextField(default=b'unknown', max_length=64)),
                ('action', models.TextField(default=b'', max_length=64)),
                ('ignore_errors', models.BooleanField(default=False)),
                ('finish_time', models.DateTimeField(null=True, blank=True)),
                ('comment', models.TextField(default=b'')),
                ('blockers', models.ManyToManyField(to='corecluster.Task', blank=True)),
                ('image', models.ForeignKey(to='corecluster.Image', null=True)),
                ('lease', models.ForeignKey(to='corecluster.Lease', null=True)),
                ('node', models.ForeignKey(to='corecluster.Node', null=True)),
                ('storage', models.ForeignKey(to='corecluster.Storage', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('_data', models.TextField(default=b'{}', help_text=b'Additional data. Leave blank if not used')),
                ('id', models.CharField(default=corecluster.models.common_models.id_generator, max_length=36, serialize=False, primary_key=True, help_text=b'API id used to identify all objects in Core')),
                ('state', models.CharField(max_length=30)),
                ('name', models.CharField(max_length=45)),
                ('description', models.CharField(max_length=512)),
                ('memory', models.IntegerField(help_text=b'Memory in megabytes')),
                ('cpu', models.IntegerField()),
                ('points', models.IntegerField()),
                ('ec2name', models.CharField(default=b't1.micro', help_text=b'Amazon EC2 template equivalent', max_length=40)),
                ('domain_type', models.CharField(default=b'hvm', max_length=64)),
                ('kernel', models.CharField(default=b'', max_length=256, null=True, help_text=b'Path to kernel used for booting virtual machine. If using default hvm type, leave it blank', blank=True)),
                ('initrd', models.CharField(default=b'', max_length=256, null=True, help_text=b'Path to initrd used for booting virtual machine. If using default hvm type, leave it blank', blank=True)),
                ('cmdline', models.CharField(default=b'', max_length=256, null=True, help_text=b'Kernel command line parameters. If using default hvm type, leave it blank', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('_data', models.TextField(default=b'{}', help_text=b'Additional data. Leave blank if not used')),
                ('id', models.CharField(default=corecluster.models.common_models.id_generator, max_length=36, serialize=False, primary_key=True, help_text=b'API id used to identify all objects in Core')),
                ('access', models.CharField(default=b'private', max_length=30, choices=[(b'private', b'private'), (b'public', b'public'), (b'group', b'group')])),
                ('name', models.CharField(default=b'', max_length=256)),
                ('token', models.TextField()),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('valid_to', models.DateTimeField(auto_now_add=True)),
                ('ignore_permissions', models.BooleanField(default=True)),
                ('group', models.ForeignKey(blank=True, to='corecluster.Group', null=True)),
                ('permissions', models.ManyToManyField(to='corecluster.Permission', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('_data', models.TextField(default=b'{}', help_text=b'Additional data. Leave blank if not used')),
                ('id', models.CharField(default=corecluster.models.common_models.id_generator, max_length=36, serialize=False, primary_key=True, help_text=b'API id used to identify all objects in Core')),
                ('state', models.CharField(max_length=30)),
                ('login', models.CharField(max_length=256)),
                ('pw_hash', models.CharField(max_length=256)),
                ('pw_seed', models.CharField(max_length=256)),
                ('name', models.CharField(max_length=256)),
                ('surname', models.CharField(max_length=256)),
                ('email', models.CharField(max_length=256)),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(to='corecluster.Group')),
                ('role', models.ForeignKey(to='corecluster.Role')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserNetwork',
            fields=[
                ('_data', models.TextField(default=b'{}', help_text=b'Additional data. Leave blank if not used')),
                ('id', models.CharField(default=corecluster.models.common_models.id_generator, max_length=36, serialize=False, primary_key=True, help_text=b'API id used to identify all objects in Core')),
                ('access', models.CharField(default=b'private', max_length=30, choices=[(b'private', b'private'), (b'public', b'public'), (b'group', b'group')])),
                ('address', models.CharField(max_length=20)),
                ('mask', models.IntegerField()),
                ('name', models.CharField(max_length=200)),
                ('is_isolated', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VM',
            fields=[
                ('_data', models.TextField(default=b'{}', help_text=b'Additional data. Leave blank if not used')),
                ('id', models.CharField(default=corecluster.models.common_models.id_generator, max_length=36, serialize=False, primary_key=True, help_text=b'API id used to identify all objects in Core')),
                ('access', models.CharField(default=b'private', max_length=30, choices=[(b'private', b'private'), (b'public', b'public'), (b'group', b'group')])),
                ('state', models.CharField(max_length=30)),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField(default=b'')),
                ('libvirt_id', models.IntegerField()),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('stop_time', models.DateTimeField(null=True, blank=True)),
                ('vnc_port', models.IntegerField()),
                ('vnc_enabled', models.BooleanField(default=False)),
                ('vnc_passwd', models.CharField(max_length=50, null=True)),
                ('save_on_destroy', models.BooleanField(default=False)),
                ('base_image', models.ForeignKey(to='corecluster.Image', null=True)),
                ('group', models.ForeignKey(blank=True, to='corecluster.Group', null=True)),
                ('node', models.ForeignKey(to='corecluster.Node')),
                ('template', models.ForeignKey(to='corecluster.Template')),
                ('user', models.ForeignKey(blank=True, to='corecluster.User', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='availablenetwork',
            name='_data',
            field=models.TextField(default=b'{}', help_text=b'Additional data. Leave blank if not used'),
        ),
        migrations.AddField(
            model_name='availablenetwork',
            name='access',
            field=models.CharField(default=b'private', max_length=30, choices=[(b'private', b'private'), (b'public', b'public'), (b'group', b'group')]),
        ),
        migrations.AddField(
            model_name='availablenetwork',
            name='address',
            field=models.CharField(default=None, max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='availablenetwork',
            name='mask',
            field=models.IntegerField(default=None, help_text=b'Network mask in short format (e.g. 24 for 255.255.255.0 network)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='availablenetwork',
            name='mode',
            field=models.CharField(default=b'public', help_text=b'Network mode.', max_length=40, choices=[(b'routed', b'routed'), (b'public', b'public'), (b'isolated', b'isolated')]),
        ),
        migrations.AddField(
            model_name='availablenetwork',
            name='state',
            field=models.CharField(default=None, max_length=30),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='availablenetwork',
            name='id',
            field=models.CharField(default=corecluster.models.common_models.id_generator, max_length=36, serialize=False, primary_key=True, help_text=b'API id used to identify all objects in Core'),
        ),
        migrations.AddField(
            model_name='usernetwork',
            name='available_network',
            field=models.ForeignKey(to='corecluster.AvailableNetwork'),
        ),
        migrations.AddField(
            model_name='usernetwork',
            name='group',
            field=models.ForeignKey(blank=True, to='corecluster.Group', null=True),
        ),
        migrations.AddField(
            model_name='usernetwork',
            name='user',
            field=models.ForeignKey(blank=True, to='corecluster.User', null=True),
        ),
        migrations.AddField(
            model_name='token',
            name='user',
            field=models.ForeignKey(blank=True, to='corecluster.User', null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='user_network',
            field=models.ForeignKey(to='corecluster.UserNetwork', null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='vm',
            field=models.ForeignKey(to='corecluster.VM', null=True),
        ),
        migrations.AddField(
            model_name='lease',
            name='user',
            field=models.ForeignKey(blank=True, to='corecluster.User', null=True),
        ),
        migrations.AddField(
            model_name='lease',
            name='user_network',
            field=models.ForeignKey(to='corecluster.UserNetwork'),
        ),
        migrations.AddField(
            model_name='lease',
            name='vm',
            field=models.ForeignKey(blank=True, to='corecluster.VM', null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='attached_to',
            field=models.ForeignKey(blank=True, to='corecluster.VM', null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='group',
            field=models.ForeignKey(blank=True, to='corecluster.Group', null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='storage',
            field=models.ForeignKey(blank=True, to='corecluster.Storage', null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='token',
            field=models.ForeignKey(blank=True, to='corecluster.Token', null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='user',
            field=models.ForeignKey(blank=True, to='corecluster.User', null=True),
        ),
        migrations.AddField(
            model_name='group',
            name='role',
            field=models.ForeignKey(to='corecluster.Role'),
        ),
        migrations.AddField(
            model_name='device',
            name='vm',
            field=models.ForeignKey(to='corecluster.VM'),
        ),
        migrations.AddField(
            model_name='availablenetwork',
            name='group',
            field=models.ForeignKey(blank=True, to='corecluster.Group', null=True),
        ),
        migrations.AddField(
            model_name='availablenetwork',
            name='user',
            field=models.ForeignKey(blank=True, to='corecluster.User', null=True),
        ),
    ]