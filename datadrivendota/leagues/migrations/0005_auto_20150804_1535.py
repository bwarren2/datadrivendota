# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0004_auto_20150530_1151'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='fantasy',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='league',
            name='private',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='league',
            name='tier',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'Amateur'), (1, b'Amateur'), (2, b'Amateur')]),
        ),
    ]
