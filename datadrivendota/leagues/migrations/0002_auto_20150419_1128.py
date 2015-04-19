# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0001_initial'),
        ('leagues', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduledmatch',
            name='team_1',
            field=models.ForeignKey(related_name='scheduled_team_1_set', to='teams.Team', null=True),
        ),
        migrations.AddField(
            model_name='scheduledmatch',
            name='team_2',
            field=models.ForeignKey(related_name='scheduled_team_2_set', to='teams.Team', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='scheduledmatch',
            unique_together=set([('league', 'game_id', 'team_1', 'team_2', 'start_time')]),
        ),
    ]
