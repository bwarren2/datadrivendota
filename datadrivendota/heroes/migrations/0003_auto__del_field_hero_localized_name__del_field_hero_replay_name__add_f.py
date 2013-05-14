# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Hero.localized_name'
        db.delete_column(u'heroes_hero', 'localized_name')

        # Deleting field 'Hero.replay_name'
        db.delete_column(u'heroes_hero', 'replay_name')

        # Adding field 'Hero.name'
        db.add_column(u'heroes_hero', 'name',
                      self.gf('django.db.models.fields.CharField')(default='TempName', max_length=200),
                      keep_default=False)

        # Adding field 'Hero.internal_name'
        db.add_column(u'heroes_hero', 'internal_name',
                      self.gf('django.db.models.fields.CharField')(default='TempInternalName', max_length=200),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Hero.localized_name'
        db.add_column(u'heroes_hero', 'localized_name',
                      self.gf('django.db.models.fields.CharField')(default='TempName', max_length=200),
                      keep_default=False)

        # Adding field 'Hero.replay_name'
        db.add_column(u'heroes_hero', 'replay_name',
                      self.gf('django.db.models.fields.CharField')(default='TempReplayName', max_length=200),
                      keep_default=False)

        # Deleting field 'Hero.name'
        db.delete_column(u'heroes_hero', 'name')

        # Deleting field 'Hero.internal_name'
        db.delete_column(u'heroes_hero', 'internal_name')


    models = {
        u'heroes.hero': {
            'Meta': {'object_name': 'Hero'},
            'alignment': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'lore': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'valve_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'heroes.role': {
            'Meta': {'object_name': 'Role'},
            'desc': ('django.db.models.fields.TextField', [], {}),
            'hero': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['heroes.Hero']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['heroes']