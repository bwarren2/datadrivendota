# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import matches.model_fields


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0008_combatlog_statelog'),
    ]

    operations = [
        migrations.AddField(
            model_name='playermatchsummary',
            name='all_data',
            field=matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True),
        ),
    ]
