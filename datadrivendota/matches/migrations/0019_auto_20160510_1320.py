# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-10 17:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0018_auto_20160418_1722'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playermatchsummary',
            name='hero_damage',
            field=models.IntegerField(null=True),
        ),
    ]
