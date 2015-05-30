# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0002_auto_20150419_1128'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='image_ugc',
            field=models.IntegerField(null=True),
        ),
    ]
