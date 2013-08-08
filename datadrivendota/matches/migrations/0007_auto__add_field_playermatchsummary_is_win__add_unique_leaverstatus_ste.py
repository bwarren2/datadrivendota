# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'PlayerMatchSummary.is_win'
        db.add_column(u'matches_playermatchsummary', 'is_win',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding unique constraint on 'LeaverStatus', fields ['steam_id']
        db.create_unique(u'matches_leaverstatus', ['steam_id'])

        # Adding unique constraint on 'LobbyType', fields ['steam_id']
        db.create_unique(u'matches_lobbytype', ['steam_id'])

        # Adding unique constraint on 'Match', fields ['match_id']
        db.create_unique(u'matches_match', ['match_id'])

        # Adding unique constraint on 'GameMode', fields ['steam_id']
        db.create_unique(u'matches_gamemode', ['steam_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'GameMode', fields ['steam_id']
        db.delete_unique(u'matches_gamemode', ['steam_id'])

        # Removing unique constraint on 'Match', fields ['match_id']
        db.delete_unique(u'matches_match', ['match_id'])

        # Removing unique constraint on 'LobbyType', fields ['steam_id']
        db.delete_unique(u'matches_lobbytype', ['steam_id'])

        # Removing unique constraint on 'LeaverStatus', fields ['steam_id']
        db.delete_unique(u'matches_leaverstatus', ['steam_id'])

        # Deleting field 'PlayerMatchSummary.is_win'
        db.delete_column(u'matches_playermatchsummary', 'is_win')


    models = {
        u'heroes.ability': {
            'Meta': {'object_name': 'Ability'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        u'heroes.hero': {
            'Meta': {'object_name': 'Hero'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'lore': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'machine_name': ('django.db.models.fields.SlugField', [], {'max_length': '200'}),
            'mugshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '150', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'role': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['heroes.Role']", 'symmetrical': 'False'}),
            'steam_id': ('django.db.models.fields.PositiveIntegerField', [], {'unique': 'True'}),
            'thumbshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'})
        },
        u'heroes.role': {
            'Meta': {'object_name': 'Role'},
            'desc': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'matches.gamemode': {
            'Meta': {'object_name': 'GameMode'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        u'matches.leaverstatus': {
            'Meta': {'object_name': 'LeaverStatus'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        u'matches.lobbytype': {
            'Meta': {'object_name': 'LobbyType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        u'matches.match': {
            'Meta': {'ordering': "['match_id']", 'object_name': 'Match'},
            'barracks_status_dire': ('django.db.models.fields.IntegerField', [], {}),
            'barracks_status_radiant': ('django.db.models.fields.IntegerField', [], {}),
            'cluster': ('django.db.models.fields.IntegerField', [], {}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'first_blood_time': ('django.db.models.fields.IntegerField', [], {}),
            'game_mode': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['matches.GameMode']"}),
            'human_players': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'league_id': ('django.db.models.fields.IntegerField', [], {}),
            'lobby_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['matches.LobbyType']"}),
            'match_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'match_seq_num': ('django.db.models.fields.IntegerField', [], {}),
            'negative_votes': ('django.db.models.fields.IntegerField', [], {}),
            'positive_votes': ('django.db.models.fields.IntegerField', [], {}),
            'radiant_win': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'season': ('django.db.models.fields.IntegerField', [], {}),
            'start_time': ('django.db.models.fields.IntegerField', [], {}),
            'tower_status_dire': ('django.db.models.fields.IntegerField', [], {}),
            'tower_status_radiant': ('django.db.models.fields.IntegerField', [], {})
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
            'item_0': ('django.db.models.fields.IntegerField', [], {}),
            'item_1': ('django.db.models.fields.IntegerField', [], {}),
            'item_2': ('django.db.models.fields.IntegerField', [], {}),
            'item_3': ('django.db.models.fields.IntegerField', [], {}),
            'item_4': ('django.db.models.fields.IntegerField', [], {}),
            'item_5': ('django.db.models.fields.IntegerField', [], {}),
            'kills': ('django.db.models.fields.IntegerField', [], {}),
            'last_hits': ('django.db.models.fields.IntegerField', [], {}),
            'leaver': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['matches.LeaverStatus']"}),
            'level': ('django.db.models.fields.IntegerField', [], {}),
            'match': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['matches.Match']"}),
            'player_slot': ('django.db.models.fields.IntegerField', [], {}),
            'steam_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['steamusers.SteamUser']"}),
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
        u'steamusers.steamuser': {
            'Meta': {'object_name': 'SteamUser'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'steam_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True'})
        }
    }

    complete_apps = ['matches']