# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Player'
        db.create_table(u'players_player', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('steam_id', self.gf('django.db.models.fields.BigIntegerField')(unique=True)),
            ('persona_name', self.gf('django.db.models.fields.TextField')()),
            ('profile_url', self.gf('django.db.models.fields.TextField')()),
            ('avatar', self.gf('django.db.models.fields.TextField')()),
            ('avatar_medium', self.gf('django.db.models.fields.TextField')()),
            ('avatar_full', self.gf('django.db.models.fields.TextField')()),
            ('updated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('last_scrape_time', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'players', ['Player'])


    def backwards(self, orm):
        # Deleting model 'Player'
        db.delete_table(u'players_player')


    models = {
        u'players.player': {
            'Meta': {'object_name': 'Player'},
            'avatar': ('django.db.models.fields.TextField', [], {}),
            'avatar_full': ('django.db.models.fields.TextField', [], {}),
            'avatar_medium': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_scrape_time': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'persona_name': ('django.db.models.fields.TextField', [], {}),
            'profile_url': ('django.db.models.fields.TextField', [], {}),
            'steam_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True'}),
            'updated': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['players']