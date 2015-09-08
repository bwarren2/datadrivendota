# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0008_livematch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='livematch',
            name='league',
            field=models.PositiveIntegerField(),
        ),
    ]
