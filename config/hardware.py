"""
This file contains default hardware set. It should be common for qemu and virtualbox,
but in case of any problems - remove listed here entries causing problems.

REMEMBER: After removing here entries, they still are in database!
"""

disk_controllers = [
    'ide',
    'sata',
    'scsi',
    'virtio',
]

default_disk_controller = disk_controllers[3]


video_devices = [
    'cirrus',
    'qxl',
    'xen',
    'vbox',
    'vga',
    'vmvga',
]
default_video_device = video_devices[1]


network_devices = [
    'e1000',
    'i82551',
    'i82557b',
    'i82559er',
    'ne2k_isa',
    'ne2k_pci',
    'pcnet',
    'rtl8139',
    'virtio',
]
default_network_device = network_devices[0]


image_formats = [
    'qcow2',
    'qcow',
    'raw',
    'vdi',
]
default_image_format = image_formats[0]
