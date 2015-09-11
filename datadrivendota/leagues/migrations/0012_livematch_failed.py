# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0011_auto_20150908_1338'),
    ]

    operations = [
        migrations.AddField(
            model_name='livematch',
            name='failed',
            field=models.BooleanField(default=False),
        ),
    ]
