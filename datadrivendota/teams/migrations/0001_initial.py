# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0001_initial'),
        ('leagues', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('steam_id', models.IntegerField(unique=True)),
                ('name', models.CharField(max_length=200, null=True)),
                ('tag', models.CharField(max_length=200, null=True)),
                ('created', models.IntegerField(null=True)),
                ('rating', models.CharField(max_length=50, null=True)),
                ('logo', models.BigIntegerField(null=True)),
                ('logo_sponsor', models.BigIntegerField(null=True)),
                ('country_code', models.CharField(max_length=10, null=True)),
                ('url', models.CharField(max_length=200, null=True)),
                ('games_played_with_current_roster', models.IntegerField(null=True)),
                ('valve_cdn_image', models.TextField(help_text=b'Steam cdn image url', null=True)),
                ('valve_cdn_sponsor_image', models.TextField(help_text=b'Steam cdn sponsor image url', null=True)),
                ('update_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('admin', models.ForeignKey(related_name='team_admin', to='players.Player', null=True)),
                ('leagues', models.ManyToManyField(to='leagues.League')),
                ('player_0', models.ForeignKey(related_name='player_0', to='players.Player', null=True)),
                ('player_1', models.ForeignKey(related_name='player_1', to='players.Player', null=True)),
                ('player_2', models.ForeignKey(related_name='player_2', to='players.Player', null=True)),
                ('player_3', models.ForeignKey(related_name='player_3', to='players.Player', null=True)),
                ('player_4', models.ForeignKey(related_name='player_4', to='players.Player', null=True)),
            ],
        ),
    ]
