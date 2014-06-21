# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'League', fields ['steam_id']
        db.create_unique(u'leagues_league', ['steam_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'League', fields ['steam_id']
        db.delete_unique(u'leagues_league', ['steam_id'])


    models = {
        u'leagues.league': {
            'Meta': {'object_name': 'League'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        u'leagues.leaguedossier': {
            'Meta': {'object_name': 'LeagueDossier'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_def': ('django.db.models.fields.IntegerField', [], {}),
            'league': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['leagues.League']", 'unique': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tournament_url': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        }
    }

    complete_apps = ['leagues']