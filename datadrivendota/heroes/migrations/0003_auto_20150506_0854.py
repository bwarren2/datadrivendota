# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def add_hero(apps, schema_editor):
    Hero = apps.get_model("heroes", "Hero")
    # Make the default "does not have hero" hero
    Hero.objects.get_or_create(steam_id=0)


def remove_hero(apps, schema_editor):
    """
    We don't want to delete the null hero; it should always be.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('heroes', '0002_auto_20150504_0759'),
    ]

    operations = [
        migrations.RunPython(add_hero, remove_hero),
    ]
