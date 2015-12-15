# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import matches.model_fields


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0007_auto_20151202_0955'),
    ]

    operations = [
        migrations.CreateModel(
            name='CombatLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('kills', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('deaths', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('last_hits', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('xp', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('healing', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('hero_dmg_taken', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('hero_dmg_dealt', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('other_dmg_taken', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('other_dmg_dealt', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('all_income', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('earned_income', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('building_income', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('courier_kill_income', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('creep_kill_income', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('hero_kill_income', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('roshan_kill_income', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('buyback_expense', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('death_expense', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('hero_xp', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('creep_xp', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('roshan_xp', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('key_bldg_dmg_dealt', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('key_bldg_kills', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('item_buys', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('playermatchsummary', models.OneToOneField(null=True, blank=True, to='matches.PlayerMatchSummary')),
            ],
        ),
        migrations.CreateModel(
            name='StateLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('agility', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('agility_total', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('strength', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('strength_total', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('intelligence', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('intelligence_total', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('damage', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('damage_taken', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('healing', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('health', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('mana', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('kills', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('deaths', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('assists', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('items', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('last_hits', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('denies', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('misses', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('lifestate', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('magic_resist_pct', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('armor', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('recent_damage', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('respawn_time', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('roshan_kills', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('nearby_creep_deaths', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('shared_gold', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('reliable_gold', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('total_earned_gold', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('unreliable_gold', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('creep_kill_gold', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('hero_kill_gold', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('income_gold', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('tower_kills', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('xp', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('position', matches.model_fields.ReplayFragmentField(null=True, upload_to=b'playermatchsummaries/replays/', blank=True)),
                ('playermatchsummary', models.OneToOneField(null=True, blank=True, to='matches.PlayerMatchSummary')),
            ],
        ),
    ]
