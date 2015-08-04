# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0005_auto_20150804_1535'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='league',
            name='private',
        ),
        migrations.AlterField(
            model_name='league',
            name='tier',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'Amateur'), (1, b'Professional'), (2, b'Premium')]),
        ),
    ]
