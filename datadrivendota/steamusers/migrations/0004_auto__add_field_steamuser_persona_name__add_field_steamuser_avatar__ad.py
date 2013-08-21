# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'SteamUser.persona_name'
        db.add_column(u'steamusers_steamuser', 'persona_name',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'SteamUser.avatar'
        db.add_column(u'steamusers_steamuser', 'avatar',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'SteamUser.avatar_medium'
        db.add_column(u'steamusers_steamuser', 'avatar_medium',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'SteamUser.avatar_full'
        db.add_column(u'steamusers_steamuser', 'avatar_full',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'SteamUser.persona_name'
        db.delete_column(u'steamusers_steamuser', 'persona_name')

        # Deleting field 'SteamUser.avatar'
        db.delete_column(u'steamusers_steamuser', 'avatar')

        # Deleting field 'SteamUser.avatar_medium'
        db.delete_column(u'steamusers_steamuser', 'avatar_medium')

        # Deleting field 'SteamUser.avatar_full'
        db.delete_column(u'steamusers_steamuser', 'avatar_full')


    models = {
        u'steamusers.steamuser': {
            'Meta': {'object_name': 'SteamUser'},
            'avatar': ('django.db.models.fields.TextField', [], {}),
            'avatar_full': ('django.db.models.fields.TextField', [], {}),
            'avatar_medium': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'persona_name': ('django.db.models.fields.TextField', [], {}),
            'steam_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True'})
        }
    }

    complete_apps = ['steamusers']