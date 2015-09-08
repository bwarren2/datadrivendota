# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0007_auto_20150901_1415'),
    ]

    operations = [
        migrations.CreateModel(
            name='LiveMatch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('steam_id', models.PositiveIntegerField()),
                ('radiant_team', models.PositiveIntegerField(null=True, blank=True)),
                ('dire_team', models.PositiveIntegerField(null=True, blank=True)),
                ('radiant_logo_ugc', models.PositiveIntegerField(null=True, blank=True)),
                ('dire_logo_ugc', models.PositiveIntegerField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('league', models.ForeignKey(to='leagues.League')),
            ],
        ),
    ]
