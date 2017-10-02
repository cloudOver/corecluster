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

from corecluster.models.core import Storage
import libvirt
from coremetry.utils import record


def _monitor_storage(storage, conn):
    st = conn.storagePoolLookupByName(storage.name)
    st.refresh()

    record.store('storage_allocation', storage.id, st.info()[2])
    record.store('storage_available', storage.id, st.info()[3])


def monitor():
    conn = libvirt.open('qemu:///system')
    for storage in Storage.objects.filter(state='ok'):
        _monitor_storage(storage, conn)

    conn.close()
