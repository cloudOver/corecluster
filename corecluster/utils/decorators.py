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


from corecluster.models.core import Permission
from corecluster.models.core import Role
from corecluster.utils.exception import CoreException
from corecluster.utils.context import Context
from corecluster.utils.encoders import CoreEncoder
from corenetwork.utils.logger import log
from corenetwork.utils import config

from django.http import HttpResponse
from django.db import transaction

from datetime import datetime
import json
import inspect
import importlib
import time

global function_doc
global decorated_functions
global ci_decorated_functions

function_doc = []
decorated_functions = set([])
ci_decorated_functions = set([])


class Register(object):
    functoin = None
    function_name = ''
    auth = ''
    log_level = ''
    log = False
    validate = {}

    def __init__(self, function, auth='token', log=False, validate={}):
        """
        :param function: parameter is passed by up-level decorator (Register)
        :param auth: authentication method (token, guest, password, node). Token authentication requires passing the
        token parameter. Guest authentication passes all parameters without checking any credentials. Password auth
        requires login and pw_hash parameters calculated from password and pw_seed parameter. Node authentication is
        used only in CI api and is based on remote IP address, auth_hash and auth_seed calculated from node's
        auth_string.
        :param log: should decorator log all messages from function? And so, in case of exceptions, all messages are
        logged
        :param validate: dictionary, which is used to validate all parameters. Keys of dictionary are parameter names.
        Values assigned to keys are functions, which should be used to validate parameters. Each validation function
        should accept two parameters: parameter name (string) and parameter value. Mind, that functions in utils.validate
        module return function. Thus, all of them are called in decorator with additional parameters (see api) to define
        additional behavior of validation (e.g. check if parameter is none)
        """
        self.function = function
        self.function_name = '%s.%s' % (function.__module__.split('.views.')[1], function.__name__)
        self.auth = auth
        self.log = log
        self.validate = validate

        self.auth_module = config.get_algorithm('AUTH')

        self.doc_func()


    def __call__(self, *args, **kwargs):
        data = json.loads(args[0].body)
        user = None
        node = None
        vm = None

        # Check all supported auth methods and fetch proper objects (user, vm or node) based on auth
        owner_id = 0
        log_type = 'user'
        try:
            if self.auth == 'token':
                user, data = self.auth_module.auth_token(data, self.function_name)
            elif self.auth == 'password':
                user, data = self.auth_module.auth_password(data, self.function_name)
            elif self.auth == 'guest':
                pass
            elif self.auth == 'node':
                node, data = self.auth_module.auth_node(data, args[0].META['REMOTE_ADDR'])
            else:
                raise Exception('unsupported_auth_method')
        except Exception as e:
            log(msg='Authentication failed. PARAMS: ' + str(args[0].body),
                exception=e,
                tags=('error', 'auth', 'call'),
                function=self.function_name)
            return self.make_response(None, {'status': str(e), 'data': None})

        # Create context with proper object (it depends on auth type - token generates user; ci generates vm, etc.)
        context = Context(user=user, node=node, vm=vm, remote_ip=args[0].META['REMOTE_ADDR'])
        data['context'] = context

        resp = {'status': 'ok', 'data': None}

        savepoint = transaction.savepoint()

        log(msg='REQUEST. PARAMS: ' + str(args[0].body), context=context, tags=('info', 'call'), function=self.function_name)

        try:
            # Verify parameters
            self.do_validation(data)

            # Call function
            start_time = time.time()
            resp['data'] = self.function(**data)

            # Commit database
            transaction.savepoint_commit(savepoint)

            # Update statistics
            if config.get('core', 'API_STATS', False):
                fname = self.function_name.replace('.', '/')
                permission = Permission.objects.filter(function=fname).first()
                permission.requests += 1
                permission.execution_time += 1000 * (time.time() - start_time)
                permission.save()

            if self.log:
                log(msg='RESPONSE. DATA: ' + str(resp['data']), tags=('info', 'call'), context=context, function=self.function_name)
        except CoreException as e:
            resp['status'] = str(e)
            transaction.savepoint_rollback(savepoint)

            log(msg=str(e), context=context, tags=('error', 'call'), function=self.function_name)
        except TypeError as e:
            resp['status'] = 'param_error'
            resp['data'] = str(e)
            transaction.savepoint_rollback(savepoint)
            log(msg=str(e), context=context, tags=('warning', 'call'), function=self.function_name)
        except Exception as e:
            resp['status'] = 'core_error'
            transaction.savepoint_rollback(savepoint)
            log(msg=str(e), context=context, tags=('error', 'critical', 'call'), function=self.function_name)

        return self.make_response(None, resp)


    def make_response(self, request, response):
        """
        Prepare valid Django's response object
        """
        resp = HttpResponse(json.dumps(response, cls=CoreEncoder, check_circular=False))
        resp['Access-Control-Allow-Origin'] = '*'
        resp['Content-type'] = 'application/json'
        return resp


    def doc_func(self):
        """ Add function description to function_doc list """
        real_params = inspect.getargs(self.function.func_code).args
        try:
            del real_params[real_params.index('context')]
            if self.auth == 'token':
                real_params.insert(0, 'token')
            elif self.auth == 'password':
                real_params.insert(0, 'login')
                real_params.insert(0, 'pw_hash')
        except:
            pass

        d = {}
        fname = self.function.__module__.split('.views.')[1].replace('.', '/') + '/' + self.function.__name__
        d['name'] = fname
        d['doc'] = self.function.func_doc
        d['params'] = real_params
        function_doc.append(d)

        # Add function to permission table if not exists yet
        if not Permission.objects.filter(function=fname).exists():
            p = Permission()
            p.function = fname
            p.save()

            try:
                default_role = Role.objects.get(name='default_role')
                default_role.add(p)
                default_role.save()
            except Exception as e:
                pass


    def do_validation(self, params):
        for param in self.validate.keys():
            if hasattr(self.validate[param], 'none') and self.validate[param].none is True and not param in params:
                continue
            if not param in params:
                raise TypeError('missing_parameter_%s' % param)

            self.validate[param](param, params[param])


def register(function=None, auth='', log=False, validate={}):
    def wrapper(function):
        r = Register(function, auth, log, validate)
        decorated_functions.add(r)
        return r

    return wrapper
