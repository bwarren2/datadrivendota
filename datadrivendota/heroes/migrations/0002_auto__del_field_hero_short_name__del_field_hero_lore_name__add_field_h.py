# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Hero.short_name'
        db.delete_column(u'heroes_hero', 'short_name')

        # Deleting field 'Hero.lore_name'
        db.delete_column(u'heroes_hero', 'lore_name')

        # Adding field 'Hero.localized_name'
        db.add_column(u'heroes_hero', 'localized_name',
                      self.gf('django.db.models.fields.CharField')(default='temp', max_length=200),
                      keep_default=False)

        # Adding field 'Hero.valve_id'
        db.add_column(u'heroes_hero', 'valve_id',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=1),
                      keep_default=False)


        # Changing field 'Hero.lore'
        db.alter_column(u'heroes_hero', 'lore', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Hero.alignment'
        db.alter_column(u'heroes_hero', 'alignment', self.gf('django.db.models.fields.CharField')(max_length=12, null=True))

    def backwards(self, orm):
        # Adding field 'Hero.short_name'
        db.add_column(u'heroes_hero', 'short_name',
                      self.gf('django.db.models.fields.CharField')(default='temp', max_length=200),
                      keep_default=False)

        # Adding field 'Hero.lore_name'
        db.add_column(u'heroes_hero', 'lore_name',
                      self.gf('django.db.models.fields.CharField')(default='Lore_name', max_length=200),
                      keep_default=False)

        # Deleting field 'Hero.localized_name'
        db.delete_column(u'heroes_hero', 'localized_name')

        # Deleting field 'Hero.valve_id'
        db.delete_column(u'heroes_hero', 'valve_id')


        # Changing field 'Hero.lore'
        db.alter_column(u'heroes_hero', 'lore', self.gf('django.db.models.fields.TextField')(default='Lore'))

        # Changing field 'Hero.alignment'
        db.alter_column(u'heroes_hero', 'alignment', self.gf('django.db.models.fields.CharField')(default='Str', max_length=2))

    models = {
        u'heroes.hero': {
            'Meta': {'object_name': 'Hero'},
            'alignment': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'localized_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'lore': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'replay_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
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