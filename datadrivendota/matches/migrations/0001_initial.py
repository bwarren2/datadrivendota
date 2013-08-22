# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Match'
        db.create_table(u'matches_match', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('steam_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('match_seq_num', self.gf('django.db.models.fields.IntegerField')()),
            ('cluster', self.gf('django.db.models.fields.IntegerField')()),
            ('start_time', self.gf('django.db.models.fields.IntegerField')()),
            ('duration', self.gf('django.db.models.fields.IntegerField')()),
            ('radiant_win', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('tower_status_radiant', self.gf('django.db.models.fields.IntegerField')()),
            ('tower_status_dire', self.gf('django.db.models.fields.IntegerField')()),
            ('barracks_status_radiant', self.gf('django.db.models.fields.IntegerField')()),
            ('barracks_status_dire', self.gf('django.db.models.fields.IntegerField')()),
            ('first_blood_time', self.gf('django.db.models.fields.IntegerField')()),
            ('human_players', self.gf('django.db.models.fields.IntegerField')()),
            ('league_id', self.gf('django.db.models.fields.IntegerField')()),
            ('positive_votes', self.gf('django.db.models.fields.IntegerField')()),
            ('negative_votes', self.gf('django.db.models.fields.IntegerField')()),
            ('lobby_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.LobbyType'])),
            ('game_mode', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.GameMode'])),
        ))
        db.send_create_signal(u'matches', ['Match'])

        # Adding model 'GameMode'
        db.create_table(u'matches_gamemode', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('steam_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'matches', ['GameMode'])

        # Adding model 'LobbyType'
        db.create_table(u'matches_lobbytype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('steam_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'matches', ['LobbyType'])

        # Adding model 'PlayerMatchSummary'
        db.create_table(u'matches_playermatchsummary', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('match', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.Match'])),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['players.Player'])),
            ('hero', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['heroes.Hero'])),
            ('player_slot', self.gf('django.db.models.fields.IntegerField')()),
            ('leaver', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.LeaverStatus'])),
            ('item_0', self.gf('django.db.models.fields.IntegerField')()),
            ('item_1', self.gf('django.db.models.fields.IntegerField')()),
            ('item_2', self.gf('django.db.models.fields.IntegerField')()),
            ('item_3', self.gf('django.db.models.fields.IntegerField')()),
            ('item_4', self.gf('django.db.models.fields.IntegerField')()),
            ('item_5', self.gf('django.db.models.fields.IntegerField')()),
            ('kills', self.gf('django.db.models.fields.IntegerField')()),
            ('deaths', self.gf('django.db.models.fields.IntegerField')()),
            ('assists', self.gf('django.db.models.fields.IntegerField')()),
            ('gold', self.gf('django.db.models.fields.IntegerField')()),
            ('last_hits', self.gf('django.db.models.fields.IntegerField')()),
            ('denies', self.gf('django.db.models.fields.IntegerField')()),
            ('gold_per_min', self.gf('django.db.models.fields.IntegerField')()),
            ('xp_per_min', self.gf('django.db.models.fields.IntegerField')()),
            ('gold_spent', self.gf('django.db.models.fields.IntegerField')()),
            ('hero_damage', self.gf('django.db.models.fields.IntegerField')()),
            ('tower_damage', self.gf('django.db.models.fields.IntegerField')()),
            ('hero_healing', self.gf('django.db.models.fields.IntegerField')()),
            ('level', self.gf('django.db.models.fields.IntegerField')()),
            ('is_win', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'matches', ['PlayerMatchSummary'])

        # Adding model 'LeaverStatus'
        db.create_table(u'matches_leaverstatus', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('steam_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'matches', ['LeaverStatus'])

        # Adding model 'SkillBuild'
        db.create_table(u'matches_skillbuild', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player_match_summary', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.PlayerMatchSummary'])),
            ('ability', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['heroes.Ability'])),
            ('time', self.gf('django.db.models.fields.IntegerField')()),
            ('level', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'matches', ['SkillBuild'])


    def backwards(self, orm):
        # Deleting model 'Match'
        db.delete_table(u'matches_match')

        # Deleting model 'GameMode'
        db.delete_table(u'matches_gamemode')

        # Deleting model 'LobbyType'
        db.delete_table(u'matches_lobbytype')

        # Deleting model 'PlayerMatchSummary'
        db.delete_table(u'matches_playermatchsummary')

        # Deleting model 'LeaverStatus'
        db.delete_table(u'matches_leaverstatus')

        # Deleting model 'SkillBuild'
        db.delete_table(u'matches_skillbuild')


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
            'Meta': {'ordering': "['steam_id']", 'object_name': 'Match'},
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
            'match_seq_num': ('django.db.models.fields.IntegerField', [], {}),
            'negative_votes': ('django.db.models.fields.IntegerField', [], {}),
            'positive_votes': ('django.db.models.fields.IntegerField', [], {}),
            'radiant_win': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_time': ('django.db.models.fields.IntegerField', [], {}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
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
            'persona_name': ('django.db.models.fields.TextField', [], {}),
            'profile_url': ('django.db.models.fields.TextField', [], {}),
            'steam_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True'}),
            'updated': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['matches']