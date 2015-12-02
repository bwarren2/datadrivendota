# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0006_playermatchsummary_replay_shard'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='radiant_win',
            field=models.NullBooleanField(),
        ),
    ]
