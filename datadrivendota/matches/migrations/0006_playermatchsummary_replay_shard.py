# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0005_match_compressed_replay'),
    ]

    operations = [
        migrations.AddField(
            model_name='playermatchsummary',
            name='replay_shard',
            field=models.FileField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True),
        ),
    ]
