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


class Context(object):
    '''
    Object of this class is passed to every View function in Core and extended views. This delivers
    access to logger, user and caller_id (user_id
    '''
    log = None
    user = None
    user_id = 0
    node = None
    node_id = 0
    vm = None
    vm_id = None

    remote_ip = None

    def __init__(self, user=None, node=None, vm=None, remote_ip=None):
        self.remote_ip = remote_ip
        self.user = user
        if user != None:
            self.user_id = user.id

        self.node = node
        if node != None:
            self.node_id = node.id

        self.vm = vm
        if vm != None:
            self.vm_id = vm.id

    def __str__(self):
        return "Context(user=%s, vm=%s, node=%s)" % (str(self.user), str(self.vm), str(self.node))