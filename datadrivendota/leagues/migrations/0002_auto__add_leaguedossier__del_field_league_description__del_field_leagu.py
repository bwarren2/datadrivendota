# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LeagueDossier'
        db.create_table(u'leagues_leaguedossier', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('league', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['leagues.League'], unique=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('tournament_url', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('item_def', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'leagues', ['LeagueDossier'])

        # Deleting field 'League.description'
        db.delete_column(u'leagues_league', 'description')

        # Deleting field 'League.tournament_url'
        db.delete_column(u'leagues_league', 'tournament_url')

        # Deleting field 'League.item_def'
        db.delete_column(u'leagues_league', 'item_def')

        # Deleting field 'League.name'
        db.delete_column(u'leagues_league', 'name')


    def backwards(self, orm):
        # Deleting model 'LeagueDossier'
        db.delete_table(u'leagues_leaguedossier')


        # User chose to not deal with backwards NULL issues for 'League.description'
        raise RuntimeError("Cannot reverse this migration. 'League.description' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'League.description'
        db.add_column(u'leagues_league', 'description',
                      self.gf('django.db.models.fields.CharField')(max_length=300),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'League.tournament_url'
        raise RuntimeError("Cannot reverse this migration. 'League.tournament_url' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'League.tournament_url'
        db.add_column(u'leagues_league', 'tournament_url',
                      self.gf('django.db.models.fields.CharField')(max_length=300),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'League.item_def'
        raise RuntimeError("Cannot reverse this migration. 'League.item_def' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'League.item_def'
        db.add_column(u'leagues_league', 'item_def',
                      self.gf('django.db.models.fields.IntegerField')(),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'League.name'
        raise RuntimeError("Cannot reverse this migration. 'League.name' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'League.name'
        db.add_column(u'leagues_league', 'name',
                      self.gf('django.db.models.fields.CharField')(max_length=200),
                      keep_default=False)


    models = {
        u'leagues.league': {
            'Meta': {'object_name': 'League'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {})
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