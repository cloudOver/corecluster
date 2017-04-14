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


import simplejson
import datetime
import importlib
from corecluster.version import version
from corecluster.cache import Cache
from corecluster.utils.context import Context
from corecluster.utils.encoders import CoreEncoder
from corenetwork.utils.logger import log
from corecluster.utils.exception import CoreException
from corenetwork.utils import config


class Model(object):
    state = 'none'
    states = []
    serializable = []

    # The name of cache hash map, which keeps all objects of this type
    container = 'undefined'

    # Fields
    id = None               # ID of object
    creation_time = None    # Creation date
    type = None             # The kind of object in container (see task model)
    
    def __init__(self, id=None, type=None, data=None, cache_key=None, user=None):
        """
        :param id: If given together with type, it gets task by id+type from cachce
        :param type: See id documentation
        :param data: If given (and no task+id pair is given), it creates task from data
        :param cache_key: Get existing task by cache_key from cache. This is alternative for id_type pair
        """

        self.logger_ctx = Context()

        if id is not None and type is not None:
            self.id = id
            self.type = type
            data = Cache.hget(self.container, self.cache_key())
            if data == '' or data is None:
                raise CoreException('cache_object_not_found')

        if cache_key is not None:
            data = Cache.hget(self.container, cache_key)
            if data == '' or data is None:
                raise CoreException('cache_object_not_found')

        if data is not None:
            deserialized = simplejson.loads(data)
            for key in deserialized:
                setattr(self, key, deserialized[key])
                if not key in self.serializable:
                    self.serializable.append(key)
        else:
            idgen = config.get_algorithm('ID_GENERATOR')
            self.id = idgen.id()
            self.creation_time = datetime.datetime.now()

        if user is not None:
            self.logger_ctx.user = user
            self.user_id = user.id
        elif hasattr(self, 'user_id') and self.user_id is not None:
            from corecluster.models.core import User
            self.logger_ctx.user = User.objects.get(id=self.user_id)


    def cache_key(self):
        '''
        Returns the key which identifies object in cache
        '''
        return "%s:%s:%s" % (version, self.type, self.id)


    def __unicode__(self):
        return self.type + '-' + self.action + '-' + self.id


    def save(self, skip_lock=False):
        '''
        Store object in cache
        '''
        l = Cache.lock(self.container + ':' + self.type + ':lock')
        if not skip_lock:
            l.acquire()

        if hasattr(self, 'user') and self.user is not None:
            self.user_id = self.user.id

        d = {}
        for field in self.serializable:
            d[field] = getattr(self, field, None)

        enc = CoreEncoder()
        r = enc.encode(d)
        Cache.hset(self.container, self.cache_key(), r)
        Cache.hset(self.container + ':' + self.type, self.cache_key(), self.state)

        if not skip_lock:
            l.release()


    def delete(self):
        '''
        Delete whole object from cache
        '''
        Cache.hdel(self.container, self.cache_key())
        Cache.hdel(self.container + ':' + self.type, self.cache_key())


    def set_state(self, state):
        if not state in self.states:
            raise CoreException('invalid_state')
        Cache.hset(self.container + ':' + self.type, self.cache_key(), state)
        self.state = state


    @property
    def to_dict(self):
        '''
        Serialize task to dictionary
        '''
        d = {}
        for field in self.serializable:
            d[field] = getattr(self, field, None)
        return d