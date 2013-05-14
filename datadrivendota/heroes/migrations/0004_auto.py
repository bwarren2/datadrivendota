# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding M2M table for field role on 'Hero'
        db.create_table(u'heroes_hero_role', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('hero', models.ForeignKey(orm[u'heroes.hero'], null=False)),
            ('role', models.ForeignKey(orm[u'heroes.role'], null=False))
        ))
        db.create_unique(u'heroes_hero_role', ['hero_id', 'role_id'])

        # Removing M2M table for field hero on 'Role'
        db.delete_table('heroes_role_hero')


    def backwards(self, orm):
        # Removing M2M table for field role on 'Hero'
        db.delete_table('heroes_hero_role')

        # Adding M2M table for field hero on 'Role'
        db.create_table(u'heroes_role_hero', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('role', models.ForeignKey(orm[u'heroes.role'], null=False)),
            ('hero', models.ForeignKey(orm[u'heroes.hero'], null=False))
        ))
        db.create_unique(u'heroes_role_hero', ['role_id', 'hero_id'])


    models = {
        u'heroes.hero': {
            'Meta': {'object_name': 'Hero'},
            'alignment': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'lore': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'role': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['heroes.Role']", 'symmetrical': 'False'}),
            'valve_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'heroes.role': {
            'Meta': {'object_name': 'Role'},
            'desc': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['heroes']