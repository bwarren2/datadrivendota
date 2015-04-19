# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ability',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('steam_id', models.IntegerField(help_text=b"Valve's internal map", unique=True)),
                ('internal_name', models.CharField(help_text=b"Valve's underscore name", max_length=150)),
                ('machine_name', models.CharField(help_text=b"Valve's underscore name, slugified", unique=True, max_length=150)),
                ('channel_time', models.CharField(help_text=b'Spaced channel time by level', max_length=150, blank=True)),
                ('damage', models.CharField(help_text=b'Spaced damage by level', max_length=150, blank=True)),
                ('damage_type', models.CharField(help_text=b'Damage type', max_length=150, blank=True)),
                ('cast_range', models.CharField(help_text=b'Spaced cast range by level', max_length=150, blank=True)),
                ('mana_cost', models.CharField(help_text=b'Spaced mana cost by level', max_length=150, blank=True)),
                ('cast_point', models.CharField(help_text=b'Spaced cast point by level', max_length=150, blank=True)),
                ('cooldown', models.CharField(help_text=b'Spaced cooldown by level', max_length=150, blank=True)),
                ('duration', models.CharField(help_text=b'Spaced duration by level', max_length=150, blank=True)),
                ('is_ultimate', models.BooleanField(default=False, help_text=b'Is this an ultimate?')),
                ('name', models.TextField(help_text=b"Valve's underscore name")),
                ('description', models.TextField(help_text=b'Tooltip', blank=True)),
                ('notes', models.TextField(help_text=b'Errata', blank=True)),
                ('lore', models.TextField(help_text=b'Flavor text', blank=True)),
                ('picture', models.ImageField(upload_to=b'heroes/img/', blank=True)),
                ('is_core', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'abilities',
            },
        ),
        migrations.CreateModel(
            name='AbilityBehavior',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('internal_name', models.CharField(help_text=b"Valve's all-caps underscore name", max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='AbilitySpecialValues',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(help_text=b"Valve's underscore name", max_length=150)),
                ('value', models.CharField(help_text=b"Valve's underscore name", max_length=150)),
                ('ability', models.ForeignKey(to='heroes.Ability')),
            ],
        ),
        migrations.CreateModel(
            name='AbilityUnitTargetFlags',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('internal_name', models.CharField(help_text=b"Valve's all-caps underscore name", max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='AbilityUnitTargetTeam',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('internal_name', models.CharField(help_text=b"Valve's all-caps underscore name", max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='AbilityUnitTargetType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('internal_name', models.CharField(help_text=b"Valve's all-caps underscore name", max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('magnitude', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Hero',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('steam_id', models.PositiveIntegerField(help_text=b"Valve's int", unique=True)),
                ('name', models.CharField(help_text=b'In-game name.', max_length=200)),
                ('machine_name', models.SlugField(help_text=b'What goes in URLs.  See slugify()', max_length=200, blank=True)),
                ('internal_name', models.CharField(help_text=b'The protobuf string for the hero', max_length=200)),
                ('lore', models.TextField(null=True)),
                ('mugshot', models.ImageField(default=b'blanks/blank_hero_mugshot.png', null=True, upload_to=b'heroes/img/')),
                ('thumbshot', models.ImageField(default=b'blanks/blank_hero_thumb.png', null=True, upload_to=b'heroes/img/')),
                ('visible', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'heroes',
            },
        ),
        migrations.CreateModel(
            name='HeroDossier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('movespeed', models.IntegerField()),
                ('max_dmg', models.IntegerField()),
                ('min_dmg', models.IntegerField()),
                ('hp', models.IntegerField(default=150, help_text=b'HP after str modification', editable=False)),
                ('mana', models.IntegerField()),
                ('hp_regen', models.FloatField()),
                ('mana_regen', models.FloatField()),
                ('armor', models.FloatField()),
                ('range', models.IntegerField()),
                ('projectile_speed', models.FloatField()),
                ('strength', models.FloatField()),
                ('agility', models.FloatField()),
                ('intelligence', models.FloatField()),
                ('strength_gain', models.FloatField()),
                ('agility_gain', models.FloatField()),
                ('intelligence_gain', models.FloatField()),
                ('alignment', models.CharField(help_text=b'Str, Int, Agi.', max_length=20, null=True, choices=[(b'strength', b'strength'), (b'agility', b'agility'), (b'intelligence', b'intelligence')])),
                ('base_atk_time', models.FloatField()),
                ('day_vision', models.IntegerField()),
                ('night_vision', models.IntegerField()),
                ('atk_point', models.FloatField()),
                ('atk_backswing', models.FloatField(default=0)),
                ('cast_point', models.FloatField(default=0)),
                ('cast_backswing', models.FloatField(default=0)),
                ('turn_rate', models.FloatField()),
                ('legs', models.IntegerField(default=0)),
                ('hero', models.OneToOneField(to='heroes.Hero')),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50, choices=[(b'LaneSupport', b'Lane Support'), (b'Carry', b'Carry'), (b'Disabler', b'Disabler'), (b'Ganker', b'Ganker'), (b'Nuker', b'Nuker'), (b'Initiator', b'Initiator'), (b'Jungler', b'Jungler'), (b'Pusher', b'Pusher'), (b'Roamer', b'Roamer'), (b'Durable', b'Durable'), (b'Escape', b'Escape'), (b'Support', b'Support')])),
                ('machine_name', models.CharField(max_length=50)),
                ('desc', models.TextField()),
                ('thumbshot', models.ImageField(null=True, upload_to=b'heroes/img/')),
            ],
        ),
        migrations.AddField(
            model_name='hero',
            name='roles',
            field=models.ManyToManyField(to='heroes.Role', through='heroes.Assignment'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='hero',
            field=models.ForeignKey(to='heroes.Hero'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='role',
            field=models.ForeignKey(to='heroes.Role'),
        ),
        migrations.AddField(
            model_name='ability',
            name='behavior',
            field=models.ManyToManyField(to='heroes.AbilityBehavior'),
        ),
        migrations.AddField(
            model_name='ability',
            name='hero',
            field=models.ForeignKey(to='heroes.Hero', null=True),
        ),
        migrations.AddField(
            model_name='ability',
            name='target_flags',
            field=models.ManyToManyField(to='heroes.AbilityUnitTargetFlags'),
        ),
        migrations.AddField(
            model_name='ability',
            name='target_team',
            field=models.ManyToManyField(to='heroes.AbilityUnitTargetTeam'),
        ),
        migrations.AddField(
            model_name='ability',
            name='target_type',
            field=models.ManyToManyField(to='heroes.AbilityUnitTargetType'),
        ),
    ]
