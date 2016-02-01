# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-12 21:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_auto_20151209_1510'),
        ('parserpipe', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='matchrequest',
            name='requester',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='requested',
            field=models.ManyToManyField(
                related_name='requesters',
                to='parserpipe.MatchRequest'
            ),
        ),
        migrations.DeleteModel(
            name='MatchRequest',
        ),
    ]