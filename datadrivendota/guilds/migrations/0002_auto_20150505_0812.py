# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('guilds', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guild',
            name='steam_id',
            field=models.IntegerField(unique=True),
        ),
    ]
