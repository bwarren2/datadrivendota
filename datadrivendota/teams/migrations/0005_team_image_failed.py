# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-05 03:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0004_auto_20150901_1522'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='image_failed',
            field=models.BooleanField(default=False),
        ),
    ]
