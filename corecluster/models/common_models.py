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
import types
import importlib
from django.db import models
from corecluster.utils.exception import CoreException
from corecluster.utils.encoders import CoreEncoder
from corecluster.cache import Cache

from corenetwork.utils import config
from corenetwork.utils.logger import log


__idgen = config.get_algorithm('ID_GENERATOR')


def id_generator():
    return __idgen.id()


class CoreModel(models.Model):
    '''
    This is base class, which should be inherited by all models used in OverCluster. This class defines also some
    additional methods, which should be used (if possible)  to manage objects.

    Create new methods as standard python methods it they are used in Core's code. If methods are used in Libvirt's
    templates, then it should be defined as properties. Methods starting with _ are usualy used to generate data
    for to_dict method.
    '''

    _data = models.TextField(default='{}', help_text="Additional data. Leave blank if not used")
    id = models.CharField(max_length=36, primary_key=True, default=id_generator, help_text="API id used to identify all objects in Core")
    last_task = models.CharField(null=True, max_length=128)

    '''
    List of serializable fields in each class. Override it in child classes. This list is used by property to_dict in
    CoreModel to serialize model class to dictionary. Put here strings with names of serializable fields (or if
    necessary class's methods decorated by @property), or 2-element lists with pairs: field name and function
    '''
    serializable = []

    '''
    List of editable fields in class. Override it in child classes. This list is used by edit method to edit certain
    fields (usualy in API methods).
    '''
    editable = []


    '''
    Logger context used for defining which log shoud store messages. In methods, use log(context=self.logger_ctx, ...)
    '''
    logger_ctx = None


    class Meta:
        app_label = 'corecluster'
        abstract = True


    def __init__(self, *args, **kwargs):
        super(CoreModel, self).__init__(*args, **kwargs)

        uid = 0
        if hasattr(self, 'user') and self.user != None:
            uid = self.user.id

        from corecluster.utils.context import Context
        self.logger_ctx = Context()
        if hasattr(self, 'user') and self.user != None:
            self.logger_ctx.user = self.user


    def data(self):
        return self.get_all_props()


    @property
    def to_dict(self):
        '''
        Serialize model object to python's dictionary. This method uses serializable list with field
        names to put them to dictionary.
        :return: Dictionary with serialized fields
        '''
        d = {}
        if not hasattr(self, 'serializable'):
            return d
        for property in self.serializable:
            key = None
            field = None

            if isinstance(property, str):
                key = property
                field = getattr(self, property, None)
            else:
                key = property[0]
                field = getattr(self, property[1], None)

            if isinstance(field, types.FunctionType) or isinstance(field, types.MethodType):
                d[key] = field()
            elif isinstance(field, CoreModel):
                d[key] = field.to_dict
            else:
                d[key] = field

        return d


    @classmethod
    def describe_model(cls):
        serializable = []
        for s in cls.serializable:
            if isinstance(s, str):
                serializable.append(s)
            elif isinstance(s, list) or isinstance(s, tuple):
                serializable.append(s[0])

        editable = []
        for s in cls.editable:
            if isinstance(s, str):
                editable.append(s)
            elif isinstance(s, list) or isinstance(s, tuple):
                editable.append(s[0])
        return {'serializable': serializable, 'editable': editable}


    def has_prop(self, key):
        """
        Check if property is present in additional dat
        :param key: Name of property
        :return: True if key is present
        """
        dec = simplejson.JSONDecoder()
        try:
            return key in dec.decode(self._data)
        except Exception as e:
            raise CoreException(str(e))


    def get_prop(self, key, default=None):
        """
        Get value of property
        :param key: String with name of the property
        :param default: Default value of property, if key is not found
        :return: Property's value
        """
        dec = simplejson.JSONDecoder()
        try:
            keys = dec.decode(self._data)
            if key in keys:
                return keys[key]
            else:
                return default
        except Exception as e:
            raise CoreException(str(e))


    def get_all_props(self):
        """
        Get dictionary with all properties
        """
        enc = simplejson.JSONDecoder()
        if self._data == '':
            self._data = '{}'

        try:
            return enc.decode(self._data)
        except Exception as e:
            raise CoreException(str(e))


    def set_prop(self, key, value):
        dec = simplejson.JSONDecoder()
        enc = CoreEncoder()
        if self._data == '':
            self._data = '{}'

        try:
            json = dec.decode(self._data)
            json[key] = value

            self._data = enc.encode(json)
        except Exception as e:
            raise CoreException(str(e))
        return self


    def set_all_props(self, props):
        enc = CoreEncoder()
        try:
            self._data = enc.encode(props)
        except Exception as e:
            raise CoreException(str(e))
        return self


    @classmethod
    def get(cls, object_id):
        try:
            obj = cls.objects.get(id=object_id)
        except Exception as e:
            raise CoreException('object_not_found')

        return obj


    @classmethod
    def get_list(cls, criteria={'id__isnull': False}, exclude={'id__isnull': True}, order_by=['id']):
        """
        Get list of objects optionaly filtered by criteria
        :param user_id: id of owner
        :param criteria: django dictionary with criteria (e.g. name="abcd")
        :param order_by: python list with field names, which will sort objects. By default this is id
        :return: Queryset or empty python's list
        """
        try:
            return cls.objects.filter(**criteria).exclude(**exclude).order_by(*order_by)
        except:
            return []


    def get_tasks(self):
        """
        Get list of blocking and not finished tasks
        """
        from corecluster.cache.task import Task
        from corecluster.cache import Cache

        tasks = self.get_prop('tasks', [])
        # TODO: Lock
        present_tasks = []
        cache_tasks = Cache.hkeys(Task.container)
        for task in tasks:
            if task in cache_tasks:
                present_tasks.append(task)
        self.set_prop('tasks', present_tasks)

        return [Task(cache_key=task_id).to_dict for task_id in present_tasks]


class UserMixin(models.Model):
    '''
    Inherit this class to create models, which should have "user" field, like VM or Image.
    This allows you to keep all models simpler
    '''

    object_access = [
        'private',
        'public',
        'group',
    ]
    user = models.ForeignKey('User', null=True, blank=True)
    group = models.ForeignKey('Group', null=True, blank=True)
    access = models.CharField(max_length=30, choices=[(k, k) for k in object_access], default='private')


    class Meta:
        app_label = 'corecluster'
        abstract = True


    @classmethod
    def get(cls, user_id, object_id):
        """
        Use this function to get object from database. This is wrapper for get_object from auth algorithm. It should
        respect ownership and group permissions of object. It may behave in different way if administrator use other
        auth driver.
        :param user_id: User's id, who wants to get object from DB
        :param object_id: Object ID, which is picked up from DB
        """

        auth_driver = config.get_algorithm('AUTH')
        return auth_driver.get_object(cls, user_id, object_id)


    @classmethod
    def get_list(cls, user_id, criteria={'id__isnull': False}, exclude={'id__isnull': True}, order_by=['id']):
        """
        Use this function to get list of objects from database. This is wrapper to get_list from auth algorithm. It
        should respect ownership and group permissions. It may behave in different way if administrator use other
        auth driver.
        :param user_id: id of owner
        :param criteria: django dictionary with criteria (e.g. name="abcd")
        :param order_by: python list with field names, which will sort objects. By default this is id
        :return: Queryset or empty python's list
        """
        auth_driver = config.get_algorithm('AUTH')
        return auth_driver.get_list(cls, user_id, criteria, exclude, order_by)


    def edit(self, context=None, **kwargs):
        '''
        Edit fields allowed by editable list.
        '''
        l = Cache.lock('db:' + self.__class__.__name__ + ':' + self.id + ':lock')
        l.acquire()

        if hasattr(self, 'user_id') and hasattr(context, 'user_id') and self.user_id != context.user_id:
            l.release()
            raise CoreException('not_owner')

        for field in self.editable:
            if isinstance(field, str):
                if field in kwargs.keys():
                    log(msg="Updating field %s" % field[0], context=self.logger_ctx)
                    setattr(self, field, kwargs[field])
            if isinstance(field, list):
                if field[0] in kwargs.keys():
                    # First, validate this param
                    field[1](field[0], kwargs[field[0]])
                    log(msg="Updating field %s" % field[0], context=self.logger_ctx)
                    setattr(self, field[0], kwargs[field[0]])
        self.save()

        l.release()


    def remove(self, context):
        '''
        Use this method to gently remove object from database with respect to access field
        '''
        if hasattr(self, 'user_id') and hasattr(context, 'user_id') and self.user_id != context.user_id:
            raise CoreException('not_owner')

        self.delete()


class StateMixin(models.Model):
    '''
    Inherit this class to create models, which have state, like Task or Virtual Machine (VM). This allows you to keep
    all models simpler. Override states list by list of your model states and place default state name in default_state
    field. Use also set_state and in_state(s) methods to making operations on entities. You could override this methods
    e.g. to implement state transition machine.
    '''
    states = []
    default_state = ''
    state = models.CharField(max_length=30)


    class Meta:
        app_label = 'corecluster'
        abstract = True


    def save(self, *args, **kwargs):
        if self.state == '' or self.state is None:
            self.state = self.default_state

        super(StateMixin, self).save(*args, **kwargs)


    def set_state(self, state):
        """
        Update object's state. This method doesnt save model!
        """
        l = Cache.lock('db:' + self.__class__.__name__ + ':' + self.id + ':lock')
        l.acquire()

        if state not in self.states:
            l.release()
            raise CoreException('invalid_state_%s' % state)
        self.state = state
        self.save()

        l.release()


    def in_state(self, state):
        """
        Check if object is in given state
        """
        if state not in self.states:
            raise CoreException('invalid_state_%s' % state)

        return self.state == state


    def in_states(self, states):
        """
        Check if object is in one of given states. Check if all given states are valid for this object
        """
        for state in states:
            if not state in self.states:
                raise CoreException('invalid_state_%s' % state)

        return self.state in states
