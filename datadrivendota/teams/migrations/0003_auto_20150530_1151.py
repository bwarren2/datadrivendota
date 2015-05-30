# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0002_team_image_ugc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='image_ugc',
            field=models.BigIntegerField(null=True),
        ),
    ]
