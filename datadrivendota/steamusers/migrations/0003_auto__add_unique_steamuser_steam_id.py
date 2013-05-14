# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'SteamUser', fields ['steam_id']
        db.create_unique(u'steamusers_steamuser', ['steam_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'SteamUser', fields ['steam_id']
        db.delete_unique(u'steamusers_steamuser', ['steam_id'])


    models = {
        u'steamusers.steamuser': {
            'Meta': {'object_name': 'SteamUser'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'steam_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True'})
        }
    }

    complete_apps = ['steamusers']