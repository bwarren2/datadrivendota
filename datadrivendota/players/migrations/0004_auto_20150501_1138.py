# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def add_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    Player = apps.get_model("players", "Player")
    ContentType = apps.get_model("contenttypes", "ContentType")
    content_type = ContentType.objects.get_for_model(Player)

    touchp, _ = Permission.objects.get_or_create(
        name='Can see tooling/interactive stuff',
        codename='can_touch',
        content_type=content_type
    )

    touch, _ = Group.objects.get_or_create(name='touch')
    touch.permissions.add(touchp)


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0003_auto_20150501_1124'),
    ]

    operations = [
        migrations.RunPython(add_permissions)
    ]
