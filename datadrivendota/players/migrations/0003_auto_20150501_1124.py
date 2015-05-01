# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def add_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    Player = apps.get_model("players", "Player")
    ContentType = apps.get_model("contenttypes", "ContentType")
    content_type = ContentType.objects.get_for_model(Player)

    lookp, _ = Permission.objects.get_or_create(
        name='Can see public stuff',
        codename='can_look',
        content_type=content_type
    )

    look, _ = Group.objects.get_or_create(name='look')
    look.permissions.add(lookp)


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0002_auto_20150501_1119'),
    ]

    operations = [
        migrations.RunPython(add_permissions)
    ]
