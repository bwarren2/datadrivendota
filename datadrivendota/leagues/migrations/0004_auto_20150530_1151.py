# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0003_league_image_ugc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='league',
            name='image_ugc',
            field=models.BigIntegerField(null=True),
        ),
    ]
