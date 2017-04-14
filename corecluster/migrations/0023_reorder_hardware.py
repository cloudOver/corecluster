# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corecluster', '0022_template_hdd'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='disk_controller',
            field=models.CharField(default=b'virtio', max_length=10, choices=[(b'ide', b'ide'), (b'sata', b'sata'), (b'scsi', b'scsi'), (b'virtio', b'virtio')]),
        ),
        migrations.AlterField(
            model_name='image',
            name='format',
            field=models.CharField(default=b'qcow2', max_length=10, choices=[(b'qcow2', b'qcow2'), (b'qcow', b'qcow'), (b'raw', b'raw'), (b'vdi', b'vdi')]),
        ),
        migrations.AlterField(
            model_name='image',
            name='network_device',
            field=models.CharField(default=b'e1000', max_length=10, choices=[(b'e1000', b'e1000'), (b'i82551', b'i82551'), (b'i82557b', b'i82557b'), (b'i82559er', b'i82559er'), (b'ne2k_isa', b'ne2k_isa'), (b'ne2k_pci', b'ne2k_pci'), (b'pcnet', b'pcnet'), (b'rtl8139', b'rtl8139'), (b'virtio', b'virtio')]),
        ),
        migrations.AlterField(
            model_name='image',
            name='video_device',
            field=models.CharField(default=b'qxl', max_length=10, choices=[(b'cirrus', b'cirrus'), (b'qxl', b'qxl'), (b'xen', b'xen'), (b'vbox', b'vbox'), (b'vga', b'vga'), (b'vmvga', b'vmvga')]),
        ),
    ]