# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-07-12 15:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0022_auto_20160604_0121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='match_seq_num',
            field=models.BigIntegerField(blank=True, help_text=b"ID valve's play sequence", null=True),
        ),
    ]
