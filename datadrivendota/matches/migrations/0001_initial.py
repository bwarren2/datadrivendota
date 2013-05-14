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
            ('match_id', self.gf('django.db.models.fields.IntegerField')()),
            ('match_seq_num', self.gf('django.db.models.fields.IntegerField')()),
            ('start_time', self.gf('django.db.models.fields.IntegerField')()),
            ('lobby_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['matches.LobbyType'])),
        ))
        db.send_create_signal(u'matches', ['Match'])

        # Adding model 'GameMode'
        db.create_table(u'matches_gamemode', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('valve_id', self.gf('django.db.models.fields.IntegerField')()),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'matches', ['GameMode'])

        # Adding model 'LobbyType'
        db.create_table(u'matches_lobbytype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('valve_id', self.gf('django.db.models.fields.IntegerField')()),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'matches', ['LobbyType'])


    def backwards(self, orm):
        # Deleting model 'Match'
        db.delete_table(u'matches_match')

        # Deleting model 'GameMode'
        db.delete_table(u'matches_gamemode')

        # Deleting model 'LobbyType'
        db.delete_table(u'matches_lobbytype')


    models = {
        u'matches.gamemode': {
            'Meta': {'object_name': 'GameMode'},
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
        }
    }

    complete_apps = ['matches']