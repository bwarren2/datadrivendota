# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Guild'
        db.create_table(u'guilds_guild', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('steam_id', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('logo', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'guilds', ['Guild'])


    def backwards(self, orm):
        # Deleting model 'Guild'
        db.delete_table(u'guilds_guild')


    models = {
        u'guilds.guild': {
            'Meta': {'object_name': 'Guild'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['guilds']