# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ItemAttributes'
        db.create_table(u'items_itemattributes', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['items.Item'])),
            ('attr', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'items', ['ItemAttributes'])

        # Adding model 'ItemComponents'
        db.create_table(u'items_itemcomponents', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='product', to=orm['items.Item'])),
            ('ingredients', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ingredients', to=orm['items.Item'])),
        ))
        db.send_create_signal(u'items', ['ItemComponents'])

        # Deleting field 'Item.external_name'
        db.delete_column(u'items_item', 'external_name')

        # Deleting field 'Item.image'
        db.delete_column(u'items_item', 'image')

        # Adding field 'Item.thumbshot'
        db.add_column(u'items_item', 'thumbshot',
                      self.gf('django.db.models.fields.files.ImageField')(default='', max_length=100),
                      keep_default=False)

        # Adding field 'Item.mugshot'
        db.add_column(u'items_item', 'mugshot',
                      self.gf('django.db.models.fields.files.ImageField')(default='', max_length=100),
                      keep_default=False)

        # Adding field 'Item.name'
        db.add_column(u'items_item', 'name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100),
                      keep_default=False)

        # Adding field 'Item.quality'
        db.add_column(u'items_item', 'quality',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100),
                      keep_default=False)

        # Adding field 'Item.cost'
        db.add_column(u'items_item', 'cost',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Item.notes'
        db.add_column(u'items_item', 'notes',
                      self.gf('django.db.models.fields.TextField')(null=True),
                      keep_default=False)

        # Adding field 'Item.mana_cost'
        db.add_column(u'items_item', 'mana_cost',
                      self.gf('django.db.models.fields.IntegerField')(null=True),
                      keep_default=False)

        # Adding field 'Item.cooldown'
        db.add_column(u'items_item', 'cooldown',
                      self.gf('django.db.models.fields.IntegerField')(null=True),
                      keep_default=False)

        # Adding field 'Item.created'
        db.add_column(u'items_item', 'created',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # Changing field 'Item.description'
        db.alter_column(u'items_item', 'description', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Item.lore'
        db.alter_column(u'items_item', 'lore', self.gf('django.db.models.fields.TextField')(null=True))

    def backwards(self, orm):
        # Deleting model 'ItemAttributes'
        db.delete_table(u'items_itemattributes')

        # Deleting model 'ItemComponents'
        db.delete_table(u'items_itemcomponents')

        # Adding field 'Item.external_name'
        db.add_column(u'items_item', 'external_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50),
                      keep_default=False)

        # Adding field 'Item.image'
        db.add_column(u'items_item', 'image',
                      self.gf('django.db.models.fields.files.ImageField')(default='', max_length=100),
                      keep_default=False)

        # Deleting field 'Item.thumbshot'
        db.delete_column(u'items_item', 'thumbshot')

        # Deleting field 'Item.mugshot'
        db.delete_column(u'items_item', 'mugshot')

        # Deleting field 'Item.name'
        db.delete_column(u'items_item', 'name')

        # Deleting field 'Item.quality'
        db.delete_column(u'items_item', 'quality')

        # Deleting field 'Item.cost'
        db.delete_column(u'items_item', 'cost')

        # Deleting field 'Item.notes'
        db.delete_column(u'items_item', 'notes')

        # Deleting field 'Item.mana_cost'
        db.delete_column(u'items_item', 'mana_cost')

        # Deleting field 'Item.cooldown'
        db.delete_column(u'items_item', 'cooldown')

        # Deleting field 'Item.created'
        db.delete_column(u'items_item', 'created')


        # Changing field 'Item.description'
        db.alter_column(u'items_item', 'description', self.gf('django.db.models.fields.TextField')(default=''))

        # Changing field 'Item.lore'
        db.alter_column(u'items_item', 'lore', self.gf('django.db.models.fields.TextField')(default=''))

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
            'attr': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
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