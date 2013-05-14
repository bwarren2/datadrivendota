# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Hero'
        db.create_table(u'heroes_hero', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('lore_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('replay_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('alignment', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('lore', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'heroes', ['Hero'])

        # Adding model 'Role'
        db.create_table(u'heroes_role', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('desc', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'heroes', ['Role'])

        # Adding M2M table for field hero on 'Role'
        db.create_table(u'heroes_role_hero', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('role', models.ForeignKey(orm[u'heroes.role'], null=False)),
            ('hero', models.ForeignKey(orm[u'heroes.hero'], null=False))
        ))
        db.create_unique(u'heroes_role_hero', ['role_id', 'hero_id'])


    def backwards(self, orm):
        # Deleting model 'Hero'
        db.delete_table(u'heroes_hero')

        # Deleting model 'Role'
        db.delete_table(u'heroes_role')

        # Removing M2M table for field hero on 'Role'
        db.delete_table('heroes_role_hero')


    models = {
        u'heroes.hero': {
            'Meta': {'object_name': 'Hero'},
            'alignment': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lore': ('django.db.models.fields.TextField', [], {}),
            'lore_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'replay_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
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