# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('steam_id', models.IntegerField(unique=True)),
                ('name', models.CharField(max_length=200, null=True)),
                ('description', models.CharField(max_length=300, null=True)),
                ('tournament_url', models.CharField(max_length=300, null=True)),
                ('item_def', models.IntegerField(null=True)),
                ('valve_cdn_image', models.TextField(help_text=b'Steam cdn image url', null=True)),
                ('update_time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='ScheduledMatch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('game_id', models.IntegerField()),
                ('start_time', models.IntegerField(help_text=b'Start time in UTC seconds')),
                ('comment', models.TextField()),
                ('final', models.BooleanField()),
                ('league', models.ForeignKey(to='leagues.League')),
            ],
        ),
    ]
