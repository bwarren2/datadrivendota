# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0004_auto_20150729_1650'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='compressed_replay',
            field=models.FileField(null=True, upload_to=b'matches/replays/', blank=True),
        ),
    ]
