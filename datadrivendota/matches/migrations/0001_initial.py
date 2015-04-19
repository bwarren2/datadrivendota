# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0001_initial'),
        ('players', '0001_initial'),
        ('heroes', '0001_initial'),
        ('leagues', '0002_auto_20150419_1128'),
        ('items', '0001_initial'),
        ('guilds', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdditionalUnit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('unit_name', models.CharField(max_length=50)),
                ('item_0', models.ForeignKey(related_name='additem0', to='items.Item')),
                ('item_1', models.ForeignKey(related_name='additem1', to='items.Item')),
                ('item_2', models.ForeignKey(related_name='additem2', to='items.Item')),
                ('item_3', models.ForeignKey(related_name='additem3', to='items.Item')),
                ('item_4', models.ForeignKey(related_name='additem4', to='items.Item')),
                ('item_5', models.ForeignKey(related_name='additem5', to='items.Item')),
            ],
        ),
        migrations.CreateModel(
            name='GameMode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('steam_id', models.IntegerField(help_text=b"Valve's id field", unique=True, db_index=True)),
                ('description', models.CharField(help_text=b'Game mode, ie. captains', max_length=50)),
                ('is_competitive', models.BooleanField(default=False, help_text=b'Whether charts should\n        show this mode by default')),
                ('visible', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['steam_id'],
            },
        ),
        migrations.CreateModel(
            name='LeaverStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('steam_id', models.IntegerField(unique=True)),
                ('description', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ['steam_id'],
                'verbose_name': 'LeaverStatus',
                'verbose_name_plural': 'LeaverStatuses',
            },
        ),
        migrations.CreateModel(
            name='LobbyType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('steam_id', models.IntegerField(help_text=b'How the queue occurred', unique=True)),
                ('description', models.CharField(help_text=b'Queue type', max_length=50)),
            ],
            options={
                'ordering': ['steam_id'],
                'verbose_name': 'LobbyType',
                'verbose_name_plural': 'LobbyTypes',
            },
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('steam_id', models.IntegerField(help_text=b"Valve's id field", unique=True)),
                ('match_seq_num', models.IntegerField(help_text=b"ID valve's play sequence")),
                ('cluster', models.IntegerField()),
                ('start_time', models.IntegerField(help_text=b'Start time in UTC seconds')),
                ('duration', models.IntegerField()),
                ('radiant_win', models.BooleanField()),
                ('tower_status_radiant', models.IntegerField()),
                ('tower_status_dire', models.IntegerField()),
                ('barracks_status_radiant', models.IntegerField()),
                ('barracks_status_dire', models.IntegerField()),
                ('first_blood_time', models.IntegerField()),
                ('human_players', models.IntegerField()),
                ('positive_votes', models.IntegerField()),
                ('negative_votes', models.IntegerField()),
                ('skill', models.IntegerField(default=0, help_text=b'How valve denotes skill bracket.  1 is normal, 2 is high, 3 is very high, 0 is my not-assigned, 4 is Tournament')),
                ('radiant_team_complete', models.NullBooleanField()),
                ('dire_team_complete', models.NullBooleanField()),
                ('series_id', models.IntegerField(null=True)),
                ('series_type', models.IntegerField(null=True)),
                ('replay', models.FileField(null=True, upload_to=b'matches/replays/')),
                ('validity', models.IntegerField(default=0, choices=[(0, b'Unprocessed'), (1, b'Legitimate'), (2, b'Abandoned')])),
                ('dire_guild', models.ForeignKey(related_name='dire_guild', to='guilds.Guild', null=True)),
                ('dire_team', models.ForeignKey(related_name='dire_team', to='teams.Team', null=True)),
                ('game_mode', models.ForeignKey(to='matches.GameMode')),
                ('league', models.ForeignKey(to='leagues.League', null=True)),
                ('lobby_type', models.ForeignKey(help_text=b'How the game was queued', to='matches.LobbyType')),
                ('radiant_guild', models.ForeignKey(related_name='radiant_guild', to='guilds.Guild', null=True)),
                ('radiant_team', models.ForeignKey(related_name='radiant_team', to='teams.Team', null=True)),
            ],
            options={
                'ordering': ['-start_time'],
                'verbose_name_plural': 'matches',
            },
        ),
        migrations.CreateModel(
            name='PickBan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_pick', models.BooleanField()),
                ('team', models.IntegerField()),
                ('order', models.IntegerField()),
                ('hero', models.ForeignKey(to='heroes.Hero')),
                ('match', models.ForeignKey(to='matches.Match')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='PlayerMatchSummary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('player_slot', models.IntegerField()),
                ('kills', models.IntegerField()),
                ('deaths', models.IntegerField()),
                ('assists', models.IntegerField()),
                ('gold', models.IntegerField()),
                ('last_hits', models.IntegerField()),
                ('denies', models.IntegerField()),
                ('gold_per_min', models.IntegerField()),
                ('xp_per_min', models.IntegerField()),
                ('gold_spent', models.IntegerField()),
                ('hero_damage', models.IntegerField()),
                ('tower_damage', models.IntegerField()),
                ('hero_healing', models.IntegerField()),
                ('level', models.IntegerField()),
                ('is_win', models.BooleanField()),
                ('hero', models.ForeignKey(to='heroes.Hero')),
                ('item_0', models.ForeignKey(related_name='item0', to='items.Item')),
                ('item_1', models.ForeignKey(related_name='item1', to='items.Item')),
                ('item_2', models.ForeignKey(related_name='item2', to='items.Item')),
                ('item_3', models.ForeignKey(related_name='item3', to='items.Item')),
                ('item_4', models.ForeignKey(related_name='item4', to='items.Item')),
                ('item_5', models.ForeignKey(related_name='item5', to='items.Item')),
                ('leaver', models.ForeignKey(to='matches.LeaverStatus')),
                ('match', models.ForeignKey(to='matches.Match')),
                ('player', models.ForeignKey(to='players.Player')),
            ],
            options={
                'ordering': ['match', 'player_slot'],
            },
        ),
        migrations.CreateModel(
            name='SkillBuild',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.IntegerField()),
                ('level', models.IntegerField()),
                ('ability', models.ForeignKey(to='heroes.Ability')),
                ('player_match_summary', models.ForeignKey(to='matches.PlayerMatchSummary')),
            ],
            options={
                'ordering': ['player_match_summary', 'level'],
            },
        ),
        migrations.AddField(
            model_name='additionalunit',
            name='player_match_summary',
            field=models.OneToOneField(to='matches.PlayerMatchSummary'),
        ),
    ]
