# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-13 19:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0015_auto_20160211_1442'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='steam_id',
            field=models.BigIntegerField(help_text=b"Valve's id field", unique=True),
        ),
    ]