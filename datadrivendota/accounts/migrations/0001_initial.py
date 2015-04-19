# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import accounts.models
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('players', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Applicant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('steam_id', models.BigIntegerField()),
                ('email', models.EmailField(max_length=254)),
                ('interested_in_premium', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='MatchRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('match_id', models.IntegerField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='PermissionCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(default=datetime.datetime.now)),
                ('key', models.CharField(default=accounts.models.get_code, max_length=40)),
                ('upgrade_type', models.IntegerField(choices=[(1, b'User can see public parts of the site'), (2, b'User can use the private parts of the site')])),
                ('registrant', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'permissions': (('can_look', 'Can see/use public things'), ('can_touch', 'Can use private tools')),
            },
        ),
        migrations.CreateModel(
            name='PollResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('steam_id', models.BigIntegerField(null=True, blank=True)),
                ('interested_in_premium', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('track_limit', models.IntegerField(default=7)),
                ('request_limit', models.IntegerField(default=10)),
                ('following', models.ManyToManyField(related_name='quarry', to='players.Player')),
                ('player', models.OneToOneField(to='players.Player')),
                ('requested', models.ManyToManyField(to='accounts.MatchRequest', null=True)),
                ('tracking', models.ManyToManyField(related_name='feed', to='players.Player')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
