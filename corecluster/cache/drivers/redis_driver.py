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

from corenetwork.utils import config
from corecluster.cache.drivers.cache_interface import CacheInterface
import redis


class Cache(CacheInterface):
    conn = None

    def __init__(self):
        self.conn = redis.Redis(config.get('core', 'CACHE_URL'), socket_keepalive=1)

    def hset(self, name, key, value):
        return self.conn.hset(name, key, value)

    def hget(self, name, key):
        return self.conn.hget(name, key)

    def hdel(self, name, key):
        return self.conn.hdel(name, key)

    def hkeys(self, name):
        return self.conn.hkeys(name)

    def hvals(self, name):
        return self.conn.hvals(name)

    def lpop(self, name):
        return self.conn.lpop(name)

    def lpush(self, name, value):
        return self.conn.lpush(name, value)

    def lindex(self, name, index):
        return self.conn.lindex(name, index)

    def llen(self, name):
        return self.conn.llen(name)

    def lrange(self, name, first, last):
        return self.conn.lrange(name, first, last)

    def keys(self):
        return self.conn.keys()

    def delete(self, name):
        return self.conn.delete(name)

    def lock(self, name):
        return self.conn.lock(name)