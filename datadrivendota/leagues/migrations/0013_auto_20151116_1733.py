# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0012_livematch_failed'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='livematch',
            unique_together=set([('league_id', 'steam_id')]),
        ),
    ]
