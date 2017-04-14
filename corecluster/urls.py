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


import importlib
from django.conf.urls import url

from corecluster.settings import APPS
from corecluster.utils.decorators import decorated_functions
from corecluster.views.admin_site import admin_site
from corecluster.views.admin import task
from corenetwork.utils.logger import log

global decorated_functionss

try:
    for app_name in APPS:
        app = importlib.import_module(app_name).MODULE
        if 'api' in app:
            for module in app['api']:
                importlib.import_module(module)
except Exception as e:
    print('Fatal error: %s' % str(e))
    log(msg="CORE: Cannot load module", tags=('error', 'critical'), exception=e)

admin_site.disable_action('delete_selected')


urlpatterns = [
    url(r'^admin/tasks/graph/', task.graph),
    url(r'^admin/tasks/', task.task_list),
    url(r'^admin/', admin_site.urls),
]

for func in decorated_functions:
    urlpatterns.append(url(r'^%s/' % (func.function_name.replace('.', '/')), func))
