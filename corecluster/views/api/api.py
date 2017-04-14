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


from corecluster.utils.decorators import register
from corecluster.settings import APPS
import importlib

@register(auth='token')
def get_list(context):
    """
    Returns list with names and descriptions of all functions available for user.
    Each list element is a dictionary with fields:
    - name - function name (url)
    - doc - documentation for function
    - params - list of parameters for function
    """
    from corecluster.utils.decorators import function_doc
    api_modules = []
    ci_modules = []
    for app_name in APPS:
        app = importlib.import_module(app_name).MODULE
        if 'api' in app:
            api_modules.extend(app['api'])
        if 'ci' in app:
            ci_modules.extend(app['ci'])

    return {
        'functions': function_doc,
        'api_modules': api_modules,
        'ci_modules': ci_modules,
        }


@register(auth='token')
def list_functions(context):
    '''
    Get list with functions and documentations
    '''
    from corecluster.utils.decorators import function_doc
    return function_doc


@register(auth='token')
def list_api_modules(context):
    '''
    Get list of enabled API modules
    '''
    api_modules = []
    for app_name in APPS:
        app = importlib.import_module(app_name).MODULE
        if 'api' in app:
            api_modules.extend(app['api'])
    return api_modules


@register(auth='token')
def list_ci_modules(context):
    '''
    Get list of enabled CI (cluster interface api) modules
    '''
    ci_modules = []
    for app_name in APPS:
        app = importlib.import_module(app_name).MODULE
        if 'ci' in app:
            ci_modules.extend(app['ci'])
    return ci_modules


@register(auth='token')
def core_version(context):
    '''
    Get version of CoreCluster
    '''
    from corecluster import version
    return version.version
