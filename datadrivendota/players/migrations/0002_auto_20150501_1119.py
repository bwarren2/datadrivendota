# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def add_base_players(apps, schema_editor):
    Player = apps.get_model("players", "Player")
    p, _ = Player.objects.get_or_create(steam_id=70388657)
    p.save()


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_base_players)
    ]
