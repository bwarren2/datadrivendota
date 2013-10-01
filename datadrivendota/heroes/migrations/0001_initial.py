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
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('machine_name', self.gf('django.db.models.fields.SlugField')(max_length=200)),
            ('internal_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('steam_id', self.gf('django.db.models.fields.PositiveIntegerField')(unique=True)),
            ('lore', self.gf('django.db.models.fields.TextField')(null=True)),
            ('mugshot', self.gf('django.db.models.fields.files.ImageField')(max_length=150, null=True)),
            ('thumbshot', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True)),
        ))
        db.send_create_signal(u'heroes', ['Hero'])

        # Adding M2M table for field role on 'Hero'
        db.create_table(u'heroes_hero_role', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('hero', models.ForeignKey(orm[u'heroes.hero'], null=False)),
            ('role', models.ForeignKey(orm[u'heroes.role'], null=False))
        ))
        db.create_unique(u'heroes_hero_role', ['hero_id', 'role_id'])

        # Adding model 'Role'
        db.create_table(u'heroes_role', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('desc', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'heroes', ['Role'])

        # Adding model 'Ability'
        db.create_table(u'heroes_ability', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('steam_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('internal_name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal(u'heroes', ['Ability'])

        # Adding model 'HeroDossier'
        db.create_table(u'heroes_herodossier', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hero', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['heroes.Hero'], unique=True)),
            ('movespeed', self.gf('django.db.models.fields.IntegerField')()),
            ('max_dmg', self.gf('django.db.models.fields.IntegerField')()),
            ('min_dmg', self.gf('django.db.models.fields.IntegerField')()),
            ('hp', self.gf('django.db.models.fields.IntegerField')(default=150)),
            ('mana', self.gf('django.db.models.fields.IntegerField')()),
            ('hp_regen', self.gf('django.db.models.fields.FloatField')()),
            ('mana_regen', self.gf('django.db.models.fields.FloatField')()),
            ('armor', self.gf('django.db.models.fields.FloatField')()),
            ('range', self.gf('django.db.models.fields.IntegerField')()),
            ('projectile_speed', self.gf('django.db.models.fields.FloatField')()),
            ('strength', self.gf('django.db.models.fields.FloatField')()),
            ('agility', self.gf('django.db.models.fields.FloatField')()),
            ('intelligence', self.gf('django.db.models.fields.FloatField')()),
            ('strength_gain', self.gf('django.db.models.fields.FloatField')()),
            ('agility_gain', self.gf('django.db.models.fields.FloatField')()),
            ('intelligence_gain', self.gf('django.db.models.fields.FloatField')()),
            ('alignment', self.gf('django.db.models.fields.CharField')(max_length=20, null=True)),
            ('base_atk_time', self.gf('django.db.models.fields.FloatField')()),
            ('day_vision', self.gf('django.db.models.fields.IntegerField')()),
            ('night_vision', self.gf('django.db.models.fields.IntegerField')()),
            ('atk_point', self.gf('django.db.models.fields.FloatField')()),
            ('atk_backswing', self.gf('django.db.models.fields.FloatField')()),
            ('cast_point', self.gf('django.db.models.fields.FloatField')()),
            ('cast_backswing', self.gf('django.db.models.fields.FloatField')()),
            ('turn_rate', self.gf('django.db.models.fields.FloatField')()),
            ('legs', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'heroes', ['HeroDossier'])


    def backwards(self, orm):
        # Deleting model 'Hero'
        db.delete_table(u'heroes_hero')

        # Removing M2M table for field role on 'Hero'
        db.delete_table('heroes_hero_role')

        # Deleting model 'Role'
        db.delete_table(u'heroes_role')

        # Deleting model 'Ability'
        db.delete_table(u'heroes_ability')

        # Deleting model 'HeroDossier'
        db.delete_table(u'heroes_herodossier')


    models = {
        u'heroes.ability': {
            'Meta': {'object_name': 'Ability'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
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
            'thumbshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'})
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