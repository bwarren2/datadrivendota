# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-24 19:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0004_auto_20150501_1138'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='updated',
        ),
    ]
