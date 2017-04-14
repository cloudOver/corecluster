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

class CacheInterface(object):
    def hset(self, name, key, value):
        '''
        Set value for hash map in name element
        '''
        raise Exception('not implemented')

    def hget(self, name, key):
        '''
        Get value of hash map in name element
        '''
        raise Exception('not implemented')

    def hdel(self, name, key):
        '''
        Delete item in hash map by given key
        '''
        raise Exception('not implemented')

    def hkeys(self, name):
        '''
        Return list of keys from given hash map
        '''
        raise Exception('not implemented')

    def hvals(self, name):
        '''
        Return list of values from given hash map
        '''
        raise Exception('not implemented')

    def lpop(self, name):
        '''
        Remove element from list
        '''
        raise Exception('not implemented')

    def lpush(self, name, value):
        '''
        Insert element at the end of the list
        '''
        raise Exception('not implemented')

    def lindex(self, name, index):
        '''
        Return element at the position in the list
        '''
        raise Exception('not implemented')

    def llen(self, name):
        '''
        Return list length
        '''
        raise Exception('not implemented')

    def lrange(self, name, first, last):
        '''
        Return elements from list from given index range
        '''
        raise Exception('not implemented')

    def keys(self):
        '''
        List all keys in cache (containers)
        '''
        raise Exception('not implemented')

    def delete(self, name):
        '''
        Delete Cache key by name (container)
        '''
        raise Exception('not implemented')

    def lock(self, name):
        raise Exception('not implemented')