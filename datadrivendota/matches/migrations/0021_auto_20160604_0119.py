# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-04 05:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0020_auto_20160604_0014'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playermatchsummary',
            name='cluster',
        ),
        migrations.RemoveField(
            model_name='playermatchsummary',
            name='replay_salt',
        ),
        migrations.AddField(
            model_name='match',
            name='replay_salt',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
