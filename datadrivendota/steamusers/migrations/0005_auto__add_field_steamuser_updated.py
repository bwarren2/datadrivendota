# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'SteamUser.updated'
        db.add_column(u'steamusers_steamuser', 'updated',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'SteamUser.updated'
        db.delete_column(u'steamusers_steamuser', 'updated')


    models = {
        u'steamusers.steamuser': {
            'Meta': {'object_name': 'SteamUser'},
            'avatar': ('django.db.models.fields.TextField', [], {}),
            'avatar_full': ('django.db.models.fields.TextField', [], {}),
            'avatar_medium': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'persona_name': ('django.db.models.fields.TextField', [], {}),
            'steam_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True'}),
            'updated': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['steamusers']