# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'OVERWRITE_IN_CONFIG'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['/etc/corecluster/templates/'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,
        },
    },
]

ALLOWED_HOSTS = []

ATOMIC_REQUESTS = True

# Application definition

INSTALLED_APPS = [
    'corecluster',
    'corenetwork',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

DATABASE_ROUTERS = ['corenetwork.utils.db_router.BasicRouter']

ROOT_URLCONF = 'corecluster.urls'

WSGI_APPLICATION = 'corecluster.wsgi.application'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/var/lib/cloudOver/static/'


# Default algorithm set
NODE_SELECT_ALGORITHM = 'corecluster.algorithms.node.simple'
STORAGE_SELECT_ALGORITHM = 'corecluster.algorithms.storage.simple'
ID_GENERATOR = 'corecluster.algorithms.id.uuid_gen'
AUTH_METHOD = 'corecluster.algorithms.auth.db'


# Load main configuration file with Django settings
import imp
import sys
try:
    sys.dont_write_bytecode = True
    coreConfig = imp.load_source('config', '/etc/corecluster/config.py')
except Exception as e:
    print('Failed to load configuration: %s' % str(e))
    sys.exit(1)

for variable in dir(coreConfig):
    setattr(sys.modules[__name__], variable, getattr(coreConfig, variable))
