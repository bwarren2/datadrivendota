# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0009_auto_20150908_1204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='livematch',
            name='dire_logo_ugc',
            field=models.BigIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='livematch',
            name='radiant_logo_ugc',
            field=models.BigIntegerField(null=True, blank=True),
        ),
    ]
