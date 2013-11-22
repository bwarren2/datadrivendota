# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Ability.name'
        db.alter_column(u'heroes_ability', 'name', self.gf('django.db.models.fields.TextField')())

        # Changing field 'Ability.notes'
        db.alter_column(u'heroes_ability', 'notes', self.gf('django.db.models.fields.TextField')())

        # Changing field 'Ability.lore'
        db.alter_column(u'heroes_ability', 'lore', self.gf('django.db.models.fields.TextField')())

        # Changing field 'Ability.description'
        db.alter_column(u'heroes_ability', 'description', self.gf('django.db.models.fields.TextField')())

    def backwards(self, orm):

        # Changing field 'Ability.name'
        db.alter_column(u'heroes_ability', 'name', self.gf('django.db.models.fields.CharField')(max_length=150))

        # Changing field 'Ability.notes'
        db.alter_column(u'heroes_ability', 'notes', self.gf('django.db.models.fields.CharField')(max_length=150))

        # Changing field 'Ability.lore'
        db.alter_column(u'heroes_ability', 'lore', self.gf('django.db.models.fields.CharField')(max_length=150))

        # Changing field 'Ability.description'
        db.alter_column(u'heroes_ability', 'description', self.gf('django.db.models.fields.CharField')(max_length=150))

    models = {
        u'heroes.ability': {
            'Meta': {'object_name': 'Ability'},
            'behavior': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['heroes.AbilityBehavior']", 'symmetrical': 'False'}),
            'cast_point': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'cast_range': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'channel_time': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'cooldown': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'damage': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'damage_type': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'duration': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'hero': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['heroes.Hero']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'is_ultimate': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lore': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'mana_cost': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'target_flags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['heroes.AbilityUnitTargetFlags']", 'symmetrical': 'False'}),
            'target_team': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['heroes.AbilityUnitTargetTeam']", 'symmetrical': 'False'}),
            'target_type': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['heroes.AbilityUnitTargetType']", 'symmetrical': 'False'})
        },
        u'heroes.abilitybehavior': {
            'Meta': {'object_name': 'AbilityBehavior'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'heroes.abilityspecialvalues': {
            'Meta': {'object_name': 'AbilitySpecialValues'},
            'ability': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['heroes.Ability']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'heroes.abilityunittargetflags': {
            'Meta': {'object_name': 'AbilityUnitTargetFlags'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'heroes.abilityunittargetteam': {
            'Meta': {'object_name': 'AbilityUnitTargetTeam'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'heroes.abilityunittargettype': {
            'Meta': {'object_name': 'AbilityUnitTargetType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
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