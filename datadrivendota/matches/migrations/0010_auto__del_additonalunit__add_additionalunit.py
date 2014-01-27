# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'AdditonalUnit'
        db.delete_table(u'matches_additonalunit')

        # Adding model 'AdditionalUnit'
        db.create_table(u'matches_additionalunit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player_match_summary', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['matches.PlayerMatchSummary'], unique=True)),
            ('unit_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('item_0', self.gf('django.db.models.fields.related.ForeignKey')(related_name='additem0', to=orm['items.Item'])),
            ('item_1', self.gf('django.db.models.fields.related.ForeignKey')(related_name='additem1', to=orm['items.Item'])),
            ('item_2', self.gf('django.db.models.fields.related.ForeignKey')(related_name='additem2', to=orm['items.Item'])),
            ('item_3', self.gf('django.db.models.fields.related.ForeignKey')(related_name='additem3', to=orm['items.Item'])),
            ('item_4', self.gf('django.db.models.fields.related.ForeignKey')(related_name='additem4', to=orm['items.Item'])),
            ('item_5', self.gf('django.db.models.fields.related.ForeignKey')(related_name='additem5', to=orm['items.Item'])),
        ))
        db.send_create_signal(u'matches', ['AdditionalUnit'])


    def backwards(self, orm):
        # Adding model 'AdditonalUnit'
        db.create_table(u'matches_additonalunit', (
            ('unit_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('item_4', self.gf('django.db.models.fields.related.ForeignKey')(related_name='additem4', to=orm['items.Item'])),
            ('item_2', self.gf('django.db.models.fields.related.ForeignKey')(related_name='additem2', to=orm['items.Item'])),
            ('item_3', self.gf('django.db.models.fields.related.ForeignKey')(related_name='additem3', to=orm['items.Item'])),
            ('item_0', self.gf('django.db.models.fields.related.ForeignKey')(related_name='additem0', to=orm['items.Item'])),
            ('item_1', self.gf('django.db.models.fields.related.ForeignKey')(related_name='additem1', to=orm['items.Item'])),
            ('player_match_summary', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['matches.PlayerMatchSummary'], unique=True)),
            ('item_5', self.gf('django.db.models.fields.related.ForeignKey')(related_name='additem5', to=orm['items.Item'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'matches', ['AdditonalUnit'])

        # Deleting model 'AdditionalUnit'
        db.delete_table(u'matches_additionalunit')


    models = {
        u'guilds.guild': {
            'Meta': {'object_name': 'Guild'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'heroes.ability': {
            'Meta': {'object_name': 'Ability'},
            'behavior': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['heroes.AbilityBehavior']", 'symmetrical': 'False'}),
            'cast_point': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'cast_range': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'channel_time': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'cooldown': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'damage': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'damage_type': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'duration': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'hero': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['heroes.Hero']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'is_core': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_ultimate': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lore': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'mana_cost': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'target_flags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['heroes.AbilityUnitTargetFlags']", 'symmetrical': 'False'}),
            'target_team': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['heroes.AbilityUnitTargetTeam']", 'symmetrical': 'False'}),
            'target_type': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['heroes.AbilityUnitTargetType']", 'symmetrical': 'False'})
        },
        u'heroes.abilitybehavior': {
            'Meta': {'object_name': 'AbilityBehavior'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'heroes.abilityunittargetflags': {
            'Meta': {'object_name': 'AbilityUnitTargetFlags'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'heroes.abilityunittargetteam': {
            'Meta': {'object_name': 'AbilityUnitTargetTeam'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'heroes.abilityunittargettype': {
            'Meta': {'object_name': 'AbilityUnitTargetType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'heroes.assignment': {
            'Meta': {'object_name': 'Assignment'},
            'hero': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['heroes.Hero']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'magnitude': ('django.db.models.fields.IntegerField', [], {}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['heroes.Role']"})
        },
        u'heroes.hero': {
            'Meta': {'ordering': "['name']", 'object_name': 'Hero'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'lore': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'machine_name': ('django.db.models.fields.SlugField', [], {'max_length': '200'}),
            'mugshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'roles': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['heroes.Role']", 'through': u"orm['heroes.Assignment']", 'symmetrical': 'False'}),
            'steam_id': ('django.db.models.fields.PositiveIntegerField', [], {'unique': 'True'}),
            'thumbshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'heroes.role': {
            'Meta': {'object_name': 'Role'},
            'desc': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'items.item': {
            'Meta': {'object_name': 'Item'},
            'cooldown': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'cost': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'created': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'lore': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'mana_cost': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'mugshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'quality': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'thumbshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'})
        },
        u'matches.additionalunit': {
            'Meta': {'object_name': 'AdditionalUnit'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_0': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'additem0'", 'to': u"orm['items.Item']"}),
            'item_1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'additem1'", 'to': u"orm['items.Item']"}),
            'item_2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'additem2'", 'to': u"orm['items.Item']"}),
            'item_3': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'additem3'", 'to': u"orm['items.Item']"}),
            'item_4': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'additem4'", 'to': u"orm['items.Item']"}),
            'item_5': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'additem5'", 'to': u"orm['items.Item']"}),
            'player_match_summary': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['matches.PlayerMatchSummary']", 'unique': 'True'}),
            'unit_name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'matches.gamemode': {
            'Meta': {'ordering': "['steam_id']", 'object_name': 'GameMode'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_competitive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'db_index': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'matches.leaverstatus': {
            'Meta': {'ordering': "['steam_id']", 'object_name': 'LeaverStatus'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        u'matches.lobbytype': {
            'Meta': {'ordering': "['steam_id']", 'object_name': 'LobbyType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        u'matches.match': {
            'Meta': {'ordering': "['-start_time']", 'object_name': 'Match'},
            'barracks_status_dire': ('django.db.models.fields.IntegerField', [], {}),
            'barracks_status_radiant': ('django.db.models.fields.IntegerField', [], {}),
            'cluster': ('django.db.models.fields.IntegerField', [], {}),
            'dire_guild': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dire_guild'", 'null': 'True', 'to': u"orm['guilds.Guild']"}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'first_blood_time': ('django.db.models.fields.IntegerField', [], {}),
            'game_mode': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['matches.GameMode']"}),
            'human_players': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'league_id': ('django.db.models.fields.IntegerField', [], {}),
            'lobby_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['matches.LobbyType']"}),
            'match_seq_num': ('django.db.models.fields.IntegerField', [], {}),
            'negative_votes': ('django.db.models.fields.IntegerField', [], {}),
            'positive_votes': ('django.db.models.fields.IntegerField', [], {}),
            'radiant_guild': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'radiant_guild'", 'null': 'True', 'to': u"orm['guilds.Guild']"}),
            'radiant_win': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'skill': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'start_time': ('django.db.models.fields.IntegerField', [], {}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'tower_status_dire': ('django.db.models.fields.IntegerField', [], {}),
            'tower_status_radiant': ('django.db.models.fields.IntegerField', [], {}),
            'validity': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'matches.pickban': {
            'Meta': {'object_name': 'PickBan'},
            'hero': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['heroes.Hero']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_pick': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'match': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['matches.Match']", 'unique': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'team': ('django.db.models.fields.IntegerField', [], {})
        },
        u'matches.playermatchsummary': {
            'Meta': {'object_name': 'PlayerMatchSummary'},
            'assists': ('django.db.models.fields.IntegerField', [], {}),
            'deaths': ('django.db.models.fields.IntegerField', [], {}),
            'denies': ('django.db.models.fields.IntegerField', [], {}),
            'gold': ('django.db.models.fields.IntegerField', [], {}),
            'gold_per_min': ('django.db.models.fields.IntegerField', [], {}),
            'gold_spent': ('django.db.models.fields.IntegerField', [], {}),
            'hero': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['heroes.Hero']"}),
            'hero_damage': ('django.db.models.fields.IntegerField', [], {}),
            'hero_healing': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_win': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'item_0': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'item0'", 'to': u"orm['items.Item']"}),
            'item_1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'item1'", 'to': u"orm['items.Item']"}),
            'item_2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'item2'", 'to': u"orm['items.Item']"}),
            'item_3': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'item3'", 'to': u"orm['items.Item']"}),
            'item_4': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'item4'", 'to': u"orm['items.Item']"}),
            'item_5': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'item5'", 'to': u"orm['items.Item']"}),
            'kills': ('django.db.models.fields.IntegerField', [], {}),
            'last_hits': ('django.db.models.fields.IntegerField', [], {}),
            'leaver': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['matches.LeaverStatus']"}),
            'level': ('django.db.models.fields.IntegerField', [], {}),
            'match': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['matches.Match']"}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['players.Player']"}),
            'player_slot': ('django.db.models.fields.IntegerField', [], {}),
            'tower_damage': ('django.db.models.fields.IntegerField', [], {}),
            'xp_per_min': ('django.db.models.fields.IntegerField', [], {})
        },
        u'matches.skillbuild': {
            'Meta': {'object_name': 'SkillBuild'},
            'ability': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['heroes.Ability']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {}),
            'player_match_summary': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['matches.PlayerMatchSummary']"}),
            'time': ('django.db.models.fields.IntegerField', [], {})
        },
        u'players.player': {
            'Meta': {'object_name': 'Player'},
            'avatar': ('django.db.models.fields.TextField', [], {}),
            'avatar_full': ('django.db.models.fields.TextField', [], {}),
            'avatar_medium': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_scrape_time': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'persona_name': ('django.db.models.fields.TextField', [], {}),
            'profile_url': ('django.db.models.fields.TextField', [], {}),
            'steam_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'db_index': 'True'}),
            'updated': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['matches']