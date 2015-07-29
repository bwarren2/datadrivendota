# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0003_auto_20150627_1200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='replay',
            field=models.FileField(null=True, upload_to=b'matches/replays/', blank=True),
        ),
    ]
