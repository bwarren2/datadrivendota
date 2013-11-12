# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Item.cost'
        db.alter_column(u'items_item', 'cost', self.gf('django.db.models.fields.IntegerField')(null=True))
        # Deleting field 'ItemComponents.ingredients'
        db.delete_column(u'items_itemcomponents', 'ingredients_id')

        # Adding field 'ItemComponents.ingredient'
        db.add_column(u'items_itemcomponents', 'ingredient',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, related_name='ingredients', to=orm['items.Item']),
                      keep_default=False)


    def backwards(self, orm):

        # Changing field 'Item.cost'
        db.alter_column(u'items_item', 'cost', self.gf('django.db.models.fields.IntegerField')(default=0))
        # Adding field 'ItemComponents.ingredients'
        db.add_column(u'items_itemcomponents', 'ingredients',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, related_name='ingredients', to=orm['items.Item']),
                      keep_default=False)

        # Deleting field 'ItemComponents.ingredient'
        db.delete_column(u'items_itemcomponents', 'ingredient_id')


    models = {
        u'items.item': {
            'Meta': {'object_name': 'Item'},
            'cooldown': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'cost': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
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
            'ingredient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ingredients'", 'to': u"orm['items.Item']"}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'product'", 'to': u"orm['items.Item']"})
        }
    }

    complete_apps = ['items']
