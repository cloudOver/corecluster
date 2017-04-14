To add new model into Core, create new subdirectory in corecluster/models/. Inside this directory you can create new
files with database models according to Django model documentation. It is recommended to keep one model in one file,
inside your new directory. Each model class should have subclass named Meta, which defines django application name
(always is corecluster, independently of your module/plugin name). For example:

from django.db import models
class MyModel(models.Model)
    age = models.IntegerField(default=0)
    name = models.CharField(max_length=128)

    class Meta:
        app_label = 'corecluster'

All your models inside plugin's directory should be listed in configuration file, in LOAD_MODELS list. This allows
Django to find all models during installation or sync'ing database. If your new model was created after core
installation, remember to execute "cc-admin makemigrations" and then "cc-admin migrate" as cloudover
user. Sample directory structure should look like this:

models/
     |-core/
     |    |...
     |
     |-your_plugin/
                 |- __init__.py
                 |- mymodel.py (with above class)

Each database model should inherit CoreModel from models.common_models. This adds some important fields, like uuid based
identifiers, or methods to serialize and edit entitites in database.
