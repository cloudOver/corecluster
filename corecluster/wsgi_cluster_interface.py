import os
import sys
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "corecluster.settings_cluster_interface")
application = get_wsgi_application()
