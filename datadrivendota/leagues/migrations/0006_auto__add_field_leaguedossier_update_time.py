# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'LeagueDossier.update_time'
        db.add_column(u'leagues_leaguedossier', 'update_time',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'LeagueDossier.update_time'
        db.delete_column(u'leagues_leaguedossier', 'update_time')


    models = {
        u'leagues.league': {
            'Meta': {'object_name': 'League'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        u'leagues.leaguedossier': {
            'Meta': {'object_name': 'LeagueDossier'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_def': ('django.db.models.fields.IntegerField', [], {}),
            'league': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['leagues.League']", 'unique': 'True'}),
            'logo_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tournament_url': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'update_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        u'leagues.scheduledmatch': {
            'Meta': {'object_name': 'ScheduledMatch'},
            'comment': ('django.db.models.fields.TextField', [], {}),
            'final': ('django.db.models.fields.BooleanField', [], {}),
            'game_id': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'league': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['leagues.League']"}),
            'start_time': ('django.db.models.fields.IntegerField', [], {}),
            'team_1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'scheduled_team_1_set'", 'to': u"orm['teams.Team']"}),
            'team_2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'scheduled_team_2_set'", 'to': u"orm['teams.Team']"})
        },
        u'teams.team': {
            'Meta': {'object_name': 'Team'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        }
    }

    complete_apps = ['leagues']