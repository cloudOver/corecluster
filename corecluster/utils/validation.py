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


import re
import datetime


def in_list(values=[], none=False):
    def validate(param_name, param):
        if none and param is None:
            return
        if none is False and param not in values:
            raise TypeError('parameter %s has wrong value' % param_name)
        else:
            return

    validate.values = values
    validate.none = none

    return validate


def is_id(none=False):
    def validate(param_name, param):
        if none == False and param == None:
            raise TypeError('parameter %s cannot be none' % param_name)
        elif param == None:
            return
        elif not (isinstance(param, unicode) or isinstance(param, str))  or not re.match(r'^[a-fA-F0-9\-]+$', param):
            raise TypeError('parameter %s is not an id' % param_name)

    validate.none = none

    return validate


def is_string(empty=False, none=False, max_length=None):
    def validate(param_name, param):
        if max_length != None and len(param) > max_length:
            raise TypeError('parameter %s is too long' % param_name)
        if none == False and param == None:
            raise TypeError('parameter %s cannot be none' % param_name)
        elif param == None:
            return
        elif not isinstance(param, str) and not isinstance(param, unicode):
            raise TypeError('parameter %s is not a string' % param_name)
        elif empty == False and param == '':
            raise TypeError('parameter %s is empty' % param_name)

    validate.none = none
    validate.empty = empty

    return validate


def is_hostname(empty=False, none=False, max_length=None):
    def validate(param_name, param):
        if max_length != None and len(param) > max_length:
            raise TypeError('parameter %s is too long' % param_name)
        if none == False and param == None:
            raise TypeError('parameter %s cannot be none' % param_name)
        elif param == None:
            return
        elif not isinstance(param, str) and not isinstance(param, unicode):
            raise TypeError('parameter %s is not a string' % param_name)
        elif empty == False and param == '':
            raise TypeError('parameter %s is empty' % param_name)
        elif not re.match('[a-z0-9\\-]+', param):
            raise TypeError('parameter %s is not valid hostname [a-z0-9\\-' % param_name)

    validate.none = none
    validate.empty = empty

    return validate


def is_integer(none=False, is_boolean=True):
    def validate(param_name, param):
        if none == False and param == None:
            raise TypeError('parameter %s cannot be none' % param_name)
        elif param == None:
            return

        if not isinstance(param, int) and not isinstance(param, long) and not isinstance(param, float) and not isinstance(param, bool):
            raise TypeError('parameter %s is not a integer' % param_name)

    validate.none = none
    validate.is_boolean = is_boolean

    return validate


def is_dictionary(none=False, empty=False):
    def validate(param_name, param):
        if none == False and param == None:
            raise TypeError('parameter %s cannot be none' % param_name)
        elif param == None:
            return
        elif not isinstance(param, dict):
            raise TypeError('parameter %s is not a dictionary' % param_name)
        elif empty == False and len(param.keys()) == 0:
            raise TypeError('parameter %s cannot be empty dict' % param_name)

    validate.none = none
    validate.empty = empty

    return validate


def is_list(none=False, is_tuple=True, empty=False):
    def validate(param_name, param):
        if none == False and param == None:
            raise TypeError('parameter %s cannot be none' % param_name)
        elif param == None:
            return
        
        if not isinstance(param, list) or isinstance(param, tuple):
            raise TypeError('parameter %s is not a list' % param_name)


        if isinstance(param, tuple) and is_tuple == False:
            raise TypeError('parameter %s cannot be a tuple' % param_name)
        
        if empty == False and len(param) == 0:
            raise TypeError('parameter %s cannot be empty list' % param_name)

    validate.none = none
    validate.is_tuple = is_tuple
    validate.empty = empty

    return validate


def is_datetime(none=False):
    def validate(param_name, param):
        if none == False and param == None:
            raise TypeError('parameter %s cannot be none' % param_name)
        elif param == None:
            return
        if not isinstance(param, datetime.datetime):
            raise TypeError('parameter %s is not a datetime object' % param_name)

    validate.none = none

    return validate

