# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'ItemAttributes.attr'
        db.delete_column(u'items_itemattributes', 'attr')

        # Adding field 'ItemAttributes.attribute'
        db.add_column(u'items_itemattributes', 'attribute',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'ItemAttributes.attr'
        db.add_column(u'items_itemattributes', 'attr',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100),
                      keep_default=False)

        # Deleting field 'ItemAttributes.attribute'
        db.delete_column(u'items_itemattributes', 'attribute')


    models = {
        u'items.item': {
            'Meta': {'object_name': 'Item'},
            'cooldown': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'cost': ('django.db.models.fields.IntegerField', [], {}),
            'created': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'lore': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'mana_cost': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'mugshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'quality': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'thumbshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'})
        },
        u'items.itemattributes': {
            'Meta': {'object_name': 'ItemAttributes'},
            'attribute': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['items.Item']"})
        },
        u'items.itemcomponents': {
            'Meta': {'object_name': 'ItemComponents'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ingredients': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ingredients'", 'to': u"orm['items.Item']"}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'product'", 'to': u"orm['items.Item']"})
        }
    }

    complete_apps = ['items']