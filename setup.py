from distutils.core import setup
from setuptools import find_packages
from distutils.command.install import install as _install

def version():
    f = open('debian/changelog')
    v = f.readline().split()[1]
    return v[1:-1]

setup(
  name = 'corecluster',
  packages = find_packages(exclude=['config', 'config.*']),
  version = '17.10.04',
  description = 'CloudOver core IaaS system',
  author = 'Marta Nabozny',
  author_email = 'martastrzet@gmail.com',
  url = 'http://cloudover.org/corecluster/',
  download_url = 'https://github.com/cloudOver/CoreCluster/archive/master.zip',
  keywords = ['corecluster', 'cloudover', 'cloud'],
  classifiers = [],
  install_requires = ['corenetwork', 'django-timedeltafield', 'redis'],
)
