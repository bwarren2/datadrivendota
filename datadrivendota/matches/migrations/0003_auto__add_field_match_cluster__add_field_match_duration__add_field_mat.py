# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Match.cluster'
        db.add_column(u'matches_match', 'cluster',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        # Adding field 'Match.duration'
        db.add_column(u'matches_match', 'duration',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Match.radiant_win'
        db.add_column(u'matches_match', 'radiant_win',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Match.tower_status_radiant'
        db.add_column(u'matches_match', 'tower_status_radiant',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Match.tower_status_dire'
        db.add_column(u'matches_match', 'tower_status_dire',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Match.barracks_status_radiant'
        db.add_column(u'matches_match', 'barracks_status_radiant',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Match.barracks_status_dire'
        db.add_column(u'matches_match', 'barracks_status_dire',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Match.first_blood_time'
        db.add_column(u'matches_match', 'first_blood_time',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Match.human_players'
        db.add_column(u'matches_match', 'human_players',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Match.league_id'
        db.add_column(u'matches_match', 'league_id',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Match.season'
        db.add_column(u'matches_match', 'season',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Match.positive_votes'
        db.add_column(u'matches_match', 'positive_votes',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Match.negative_votes'
        db.add_column(u'matches_match', 'negative_votes',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Match.game_mode'
        db.add_column(u'matches_match', 'game_mode',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['matches.GameMode']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Match.cluster'
        db.delete_column(u'matches_match', 'cluster')

        # Deleting field 'Match.duration'
        db.delete_column(u'matches_match', 'duration')

        # Deleting field 'Match.radiant_win'
        db.delete_column(u'matches_match', 'radiant_win')

        # Deleting field 'Match.tower_status_radiant'
        db.delete_column(u'matches_match', 'tower_status_radiant')

        # Deleting field 'Match.tower_status_dire'
        db.delete_column(u'matches_match', 'tower_status_dire')

        # Deleting field 'Match.barracks_status_radiant'
        db.delete_column(u'matches_match', 'barracks_status_radiant')

        # Deleting field 'Match.barracks_status_dire'
        db.delete_column(u'matches_match', 'barracks_status_dire')

        # Deleting field 'Match.first_blood_time'
        db.delete_column(u'matches_match', 'first_blood_time')

        # Deleting field 'Match.human_players'
        db.delete_column(u'matches_match', 'human_players')

        # Deleting field 'Match.league_id'
        db.delete_column(u'matches_match', 'league_id')

        # Deleting field 'Match.season'
        db.delete_column(u'matches_match', 'season')

        # Deleting field 'Match.positive_votes'
        db.delete_column(u'matches_match', 'positive_votes')

        # Deleting field 'Match.negative_votes'
        db.delete_column(u'matches_match', 'negative_votes')

        # Deleting field 'Match.game_mode'
        db.delete_column(u'matches_match', 'game_mode_id')


    models = {
        u'heroes.ability': {
            'Meta': {'object_name': 'Ability'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'heroes.hero': {
            'Meta': {'object_name': 'Hero'},
            'alignment': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'lore': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'machine_name': ('django.db.models.fields.SlugField', [], {'max_length': '200'}),
            'mugshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '150', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'role': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['heroes.Role']", 'symmetrical': 'False'}),
            'steam_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'thumbshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'})
        },
        u'heroes.role': {
            'Meta': {'object_name': 'Role'},
            'desc': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'matches.gamemode': {
            'Meta': {'object_name': 'GameMode'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'valve_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'matches.leaverstatus': {
            'Meta': {'object_name': 'LeaverStatus'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'valve_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'matches.lobbytype': {
            'Meta': {'object_name': 'LobbyType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'valve_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'matches.match': {
            'Meta': {'object_name': 'Match'},
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
            'match_id': ('django.db.models.fields.IntegerField', [], {}),
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
            'match_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['matches.PlayerMatchSummary']"}),
            'time': ('django.db.models.fields.IntegerField', [], {})
        },
        u'steamusers.steamuser': {
            'Meta': {'object_name': 'SteamUser'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['matches']