# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AbilitySpecialValues'
        db.create_table(u'heroes_abilityspecialvalues', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ability', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['heroes.Ability'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal(u'heroes', ['AbilitySpecialValues'])

        # Adding model 'AbilityUnitTargetTeam'
        db.create_table(u'heroes_abilityunittargetteam', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('steam_name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal(u'heroes', ['AbilityUnitTargetTeam'])

        # Adding model 'AbilityUnitTargetFlags'
        db.create_table(u'heroes_abilityunittargetflags', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('steam_name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal(u'heroes', ['AbilityUnitTargetFlags'])

        # Adding model 'AbilityUnitTargetType'
        db.create_table(u'heroes_abilityunittargettype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('steam_name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal(u'heroes', ['AbilityUnitTargetType'])

        # Adding model 'AbilityBehavior'
        db.create_table(u'heroes_abilitybehavior', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('steam_name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal(u'heroes', ['AbilityBehavior'])

        # Adding M2M table for field special_values on 'Ability'
        db.create_table(u'heroes_ability_special_values', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ability', models.ForeignKey(orm[u'heroes.ability'], null=False)),
            ('abilityspecialvalues', models.ForeignKey(orm[u'heroes.abilityspecialvalues'], null=False))
        ))
        db.create_unique(u'heroes_ability_special_values', ['ability_id', 'abilityspecialvalues_id'])

        # Adding M2M table for field behavior on 'Ability'
        db.create_table(u'heroes_ability_behavior', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ability', models.ForeignKey(orm[u'heroes.ability'], null=False)),
            ('abilitybehavior', models.ForeignKey(orm[u'heroes.abilitybehavior'], null=False))
        ))
        db.create_unique(u'heroes_ability_behavior', ['ability_id', 'abilitybehavior_id'])

        # Adding M2M table for field target_flags on 'Ability'
        db.create_table(u'heroes_ability_target_flags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ability', models.ForeignKey(orm[u'heroes.ability'], null=False)),
            ('abilityunittargetflags', models.ForeignKey(orm[u'heroes.abilityunittargetflags'], null=False))
        ))
        db.create_unique(u'heroes_ability_target_flags', ['ability_id', 'abilityunittargetflags_id'])

        # Adding M2M table for field target_type on 'Ability'
        db.create_table(u'heroes_ability_target_type', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ability', models.ForeignKey(orm[u'heroes.ability'], null=False)),
            ('abilityunittargettype', models.ForeignKey(orm[u'heroes.abilityunittargettype'], null=False))
        ))
        db.create_unique(u'heroes_ability_target_type', ['ability_id', 'abilityunittargettype_id'])

        # Adding M2M table for field target_team on 'Ability'
        db.create_table(u'heroes_ability_target_team', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ability', models.ForeignKey(orm[u'heroes.ability'], null=False)),
            ('abilityunittargetteam', models.ForeignKey(orm[u'heroes.abilityunittargetteam'], null=False))
        ))
        db.create_unique(u'heroes_ability_target_team', ['ability_id', 'abilityunittargetteam_id'])


    def backwards(self, orm):
        # Deleting model 'AbilitySpecialValues'
        db.delete_table(u'heroes_abilityspecialvalues')

        # Deleting model 'AbilityUnitTargetTeam'
        db.delete_table(u'heroes_abilityunittargetteam')

        # Deleting model 'AbilityUnitTargetFlags'
        db.delete_table(u'heroes_abilityunittargetflags')

        # Deleting model 'AbilityUnitTargetType'
        db.delete_table(u'heroes_abilityunittargettype')

        # Deleting model 'AbilityBehavior'
        db.delete_table(u'heroes_abilitybehavior')

        # Removing M2M table for field special_values on 'Ability'
        db.delete_table('heroes_ability_special_values')

        # Removing M2M table for field behavior on 'Ability'
        db.delete_table('heroes_ability_behavior')

        # Removing M2M table for field target_flags on 'Ability'
        db.delete_table('heroes_ability_target_flags')

        # Removing M2M table for field target_type on 'Ability'
        db.delete_table('heroes_ability_target_type')

        # Removing M2M table for field target_team on 'Ability'
        db.delete_table('heroes_ability_target_team')


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
            'duration': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'is_ultimate': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mana_cost': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'special_values': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'special_value_pairs'", 'symmetrical': 'False', 'to': u"orm['heroes.AbilitySpecialValues']"}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'target_flags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['heroes.AbilityUnitTargetFlags']", 'symmetrical': 'False'}),
            'target_team': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['heroes.AbilityUnitTargetTeam']", 'symmetrical': 'False'}),
            'target_type': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['heroes.AbilityUnitTargetType']", 'symmetrical': 'False'})
        },
        u'heroes.abilitybehavior': {
            'Meta': {'object_name': 'AbilityBehavior'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'steam_name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
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
            'steam_name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'heroes.abilityunittargetteam': {
            'Meta': {'object_name': 'AbilityUnitTargetTeam'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'steam_name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'heroes.abilityunittargettype': {
            'Meta': {'object_name': 'AbilityUnitTargetType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'steam_name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
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