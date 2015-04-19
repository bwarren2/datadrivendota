# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import players.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('steam_id', models.BigIntegerField(help_text=b"Valve's internal map", unique=True, db_index=True, validators=[players.validators.validate_32bit])),
                ('persona_name', models.TextField(help_text=b'Your name on steam')),
                ('profile_url', models.TextField(help_text=b'Steam profile URL')),
                ('avatar', models.TextField(help_text=b'Tiny avatar image url')),
                ('avatar_medium', models.TextField(help_text=b'Medium avatar image url')),
                ('avatar_full', models.TextField(help_text=b'Big avatar image url')),
                ('pro_name', models.TextField(help_text=b'If this is a pro, what are they known as?', null=True)),
                ('updated', models.BooleanField(default=False, help_text=b'Do we update this person and scrape them?')),
                ('last_scrape_time', models.IntegerField(default=0, help_text=b'Unix time of last match scrape start')),
            ],
        ),
    ]
