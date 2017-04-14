# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def migrate_hashes(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    User = apps.get_model("corecluster", "User")
    for u in User.objects.all():
        if not u.pw_hash.startswith('sha1:') and not u.pw_hash.startswith('sha512:'):
            u.pw_hash = 'sha1:' + u.pw_hash
            u.save()

class Migration(migrations.Migration):

    dependencies = [
        ('corecluster', '0045_websocket_proxy'),
    ]

    operations = [
        migrations.RunPython(migrate_hashes),
    ]