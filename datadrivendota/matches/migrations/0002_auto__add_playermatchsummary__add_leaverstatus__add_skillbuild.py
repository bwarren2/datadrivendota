# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PlayerMatchSummary'
        db.create_table(u'matches_playermatchsummary', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('steam_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['steamusers.SteamUser'])),
            ('player_slot', self.gf('django.db.models.fields.IntegerField')()),
            ('hero', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['heroes.Hero'])),
            ('item_0', self.gf('django.db.models.fields.IntegerField')()),
            ('item_1', self.gf('django.db.models.fields.IntegerField')()),
            ('item_2', self.gf('django.db.models.fields.IntegerField')()),
            ('item_3', self.gf('django.db.models.fields.IntegerField')()),
            ('item_4', self.gf('django.db.models.fields.IntegerField')()),
            ('item_5', self.gf('django.db.models.fields.IntegerField')()),
            ('kills', self.gf('django.db.models.fields.IntegerField')()),
            ('deaths', self.gf('django.db.models.fields.IntegerField')()),
            ('assists', self.gf('django.db.models.fields.IntegerField')()),
            ('leaver', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.LeaverStatus'])),
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
        ))
        db.send_create_signal(u'matches', ['PlayerMatchSummary'])

        # Adding model 'LeaverStatus'
        db.create_table(u'matches_leaverstatus', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('valve_id', self.gf('django.db.models.fields.IntegerField')()),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'matches', ['LeaverStatus'])

        # Adding model 'SkillBuild'
        db.create_table(u'matches_skillbuild', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('match_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.PlayerMatchSummary'])),
            ('ability', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['heroes.Ability'])),
            ('time', self.gf('django.db.models.fields.IntegerField')()),
            ('level', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'matches', ['SkillBuild'])


    def backwards(self, orm):
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lobby_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['matches.LobbyType']"}),
            'match_id': ('django.db.models.fields.IntegerField', [], {}),
            'match_seq_num': ('django.db.models.fields.IntegerField', [], {}),
            'start_time': ('django.db.models.fields.IntegerField', [], {})
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