# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Guild.logo'
        db.alter_column(u'guilds_guild', 'logo', self.gf('django.db.models.fields.BigIntegerField')())

    def backwards(self, orm):

        # Changing field 'Guild.logo'
        db.alter_column(u'guilds_guild', 'logo', self.gf('django.db.models.fields.IntegerField')())

    models = {
        u'guilds.guild': {
            'Meta': {'object_name': 'Guild'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.BigIntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['guilds']