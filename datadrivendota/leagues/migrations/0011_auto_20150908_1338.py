# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0010_auto_20150908_1206'),
    ]

    operations = [
        migrations.RenameField(
            model_name='livematch',
            old_name='league',
            new_name='league_id',
        ),
    ]
