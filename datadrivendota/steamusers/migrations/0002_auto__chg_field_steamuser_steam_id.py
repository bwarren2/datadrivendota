# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'SteamUser.steam_id'
        db.alter_column(u'steamusers_steamuser', 'steam_id', self.gf('django.db.models.fields.BigIntegerField')())

    def backwards(self, orm):

        # Changing field 'SteamUser.steam_id'
        db.alter_column(u'steamusers_steamuser', 'steam_id', self.gf('django.db.models.fields.IntegerField')())

    models = {
        u'steamusers.steamuser': {
            'Meta': {'object_name': 'SteamUser'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'steam_id': ('django.db.models.fields.BigIntegerField', [], {})
        }
    }

    complete_apps = ['steamusers']