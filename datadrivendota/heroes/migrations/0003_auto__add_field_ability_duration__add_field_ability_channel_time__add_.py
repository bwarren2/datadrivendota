# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Ability.duration'
        db.add_column(u'heroes_ability', 'duration',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=150, blank=True),
                      keep_default=False)

        # Adding field 'Ability.channel_time'
        db.add_column(u'heroes_ability', 'channel_time',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=150, blank=True),
                      keep_default=False)

        # Adding field 'Ability.damage'
        db.add_column(u'heroes_ability', 'damage',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=150, blank=True),
                      keep_default=False)

        # Adding field 'Ability.is_ultimate'
        db.add_column(u'heroes_ability', 'is_ultimate',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Ability.damage_type'
        db.add_column(u'heroes_ability', 'damage_type',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=150, blank=True),
                      keep_default=False)

        # Adding field 'Ability.cast_range'
        db.add_column(u'heroes_ability', 'cast_range',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=150, blank=True),
                      keep_default=False)

        # Adding field 'Ability.mana_cost'
        db.add_column(u'heroes_ability', 'mana_cost',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=150, blank=True),
                      keep_default=False)

        # Adding field 'Ability.cast_point'
        db.add_column(u'heroes_ability', 'cast_point',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=150, blank=True),
                      keep_default=False)

        # Adding field 'Ability.cooldown'
        db.add_column(u'heroes_ability', 'cooldown',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=150, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Ability.duration'
        db.delete_column(u'heroes_ability', 'duration')

        # Deleting field 'Ability.channel_time'
        db.delete_column(u'heroes_ability', 'channel_time')

        # Deleting field 'Ability.damage'
        db.delete_column(u'heroes_ability', 'damage')

        # Deleting field 'Ability.is_ultimate'
        db.delete_column(u'heroes_ability', 'is_ultimate')

        # Deleting field 'Ability.damage_type'
        db.delete_column(u'heroes_ability', 'damage_type')

        # Deleting field 'Ability.cast_range'
        db.delete_column(u'heroes_ability', 'cast_range')

        # Deleting field 'Ability.mana_cost'
        db.delete_column(u'heroes_ability', 'mana_cost')

        # Deleting field 'Ability.cast_point'
        db.delete_column(u'heroes_ability', 'cast_point')

        # Deleting field 'Ability.cooldown'
        db.delete_column(u'heroes_ability', 'cooldown')


    models = {
        u'heroes.ability': {
            'Meta': {'object_name': 'Ability'},
            'cast_point': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'cast_range': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'channel_time': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'cooldown': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'damage': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'damage_type': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'duration': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'is_ultimate': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mana_cost': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        u'heroes.hero': {
            'Meta': {'ordering': "['name']", 'object_name': 'Hero'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'lore': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'machine_name': ('django.db.models.fields.SlugField', [], {'max_length': '200'}),
            'mugshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '150', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'role': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['heroes.Role']", 'symmetrical': 'False'}),
            'steam_id': ('django.db.models.fields.PositiveIntegerField', [], {'unique': 'True'}),
            'thumbshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'heroes.herodossier': {
            'Meta': {'object_name': 'HeroDossier'},
            'agility': ('django.db.models.fields.FloatField', [], {}),
            'agility_gain': ('django.db.models.fields.FloatField', [], {}),
            'alignment': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'armor': ('django.db.models.fields.FloatField', [], {}),
            'atk_backswing': ('django.db.models.fields.FloatField', [], {}),
            'atk_point': ('django.db.models.fields.FloatField', [], {}),
            'base_atk_time': ('django.db.models.fields.FloatField', [], {}),
            'cast_backswing': ('django.db.models.fields.FloatField', [], {}),
            'cast_point': ('django.db.models.fields.FloatField', [], {}),
            'day_vision': ('django.db.models.fields.IntegerField', [], {}),
            'hero': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['heroes.Hero']", 'unique': 'True'}),
            'hp': ('django.db.models.fields.IntegerField', [], {'default': '150'}),
            'hp_regen': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intelligence': ('django.db.models.fields.FloatField', [], {}),
            'intelligence_gain': ('django.db.models.fields.FloatField', [], {}),
            'legs': ('django.db.models.fields.IntegerField', [], {}),
            'mana': ('django.db.models.fields.IntegerField', [], {}),
            'mana_regen': ('django.db.models.fields.FloatField', [], {}),
            'max_dmg': ('django.db.models.fields.IntegerField', [], {}),
            'min_dmg': ('django.db.models.fields.IntegerField', [], {}),
            'movespeed': ('django.db.models.fields.IntegerField', [], {}),
            'night_vision': ('django.db.models.fields.IntegerField', [], {}),
            'projectile_speed': ('django.db.models.fields.FloatField', [], {}),
            'range': ('django.db.models.fields.IntegerField', [], {}),
            'strength': ('django.db.models.fields.FloatField', [], {}),
            'strength_gain': ('django.db.models.fields.FloatField', [], {}),
            'turn_rate': ('django.db.models.fields.FloatField', [], {})
        },
        u'heroes.role': {
            'Meta': {'object_name': 'Role'},
            'desc': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        }
    }

    complete_apps = ['heroes']