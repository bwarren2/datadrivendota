# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'League'
        db.create_table(u'leagues_league', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('steam_id', self.gf('django.db.models.fields.IntegerField')()),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('tournament_url', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('item_def', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'leagues', ['League'])


    def backwards(self, orm):
        # Deleting model 'League'
        db.delete_table(u'leagues_league')


    models = {
        u'leagues.league': {
            'Meta': {'object_name': 'League'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_def': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {}),
            'tournament_url': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        }
    }

    complete_apps = ['leagues']