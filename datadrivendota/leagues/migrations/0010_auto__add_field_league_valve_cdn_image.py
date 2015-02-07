# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'League.valve_cdn_image'
        db.add_column(u'leagues_league', 'valve_cdn_image',
                      self.gf('django.db.models.fields.TextField')(null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'League.valve_cdn_image'
        db.delete_column(u'leagues_league', 'valve_cdn_image')


    models = {
        u'leagues.league': {
            'Meta': {'object_name': 'League'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_def': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'logo_image': ('django.db.models.fields.files.ImageField', [], {'default': "'blank_team.png'", 'max_length': '100', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'tournament_url': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True'}),
            'update_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'valve_cdn_image': ('django.db.models.fields.TextField', [], {'null': 'True'})
        },
        u'leagues.scheduledmatch': {
            'Meta': {'unique_together': "(('league', 'game_id', 'team_1', 'team_2', 'start_time'),)", 'object_name': 'ScheduledMatch'},
            'comment': ('django.db.models.fields.TextField', [], {}),
            'final': ('django.db.models.fields.BooleanField', [], {}),
            'game_id': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'league': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['leagues.League']"}),
            'start_time': ('django.db.models.fields.IntegerField', [], {}),
            'team_1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'scheduled_team_1_set'", 'null': 'True', 'to': u"orm['teams.Team']"}),
            'team_2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'scheduled_team_2_set'", 'null': 'True', 'to': u"orm['teams.Team']"})
        },
        u'players.player': {
            'Meta': {'object_name': 'Player'},
            'avatar': ('django.db.models.fields.TextField', [], {}),
            'avatar_full': ('django.db.models.fields.TextField', [], {}),
            'avatar_medium': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_scrape_time': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'persona_name': ('django.db.models.fields.TextField', [], {}),
            'pro_name': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'profile_url': ('django.db.models.fields.TextField', [], {}),
            'steam_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'db_index': 'True'}),
            'updated': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'teams.team': {
            'Meta': {'object_name': 'Team'},
            'admin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'team_admin'", 'null': 'True', 'to': u"orm['players.Player']"}),
            'country_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'created': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'games_played_with_current_roster': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'leagues': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['leagues.League']", 'symmetrical': 'False'}),
            'logo': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'logo_image': ('django.db.models.fields.files.ImageField', [], {'default': "'blank_team.png'", 'max_length': '100', 'null': 'True'}),
            'logo_sponsor': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'logo_sponsor_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'player_0': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'player_0'", 'null': 'True', 'to': u"orm['players.Player']"}),
            'player_1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'player_1'", 'null': 'True', 'to': u"orm['players.Player']"}),
            'player_2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'player_2'", 'null': 'True', 'to': u"orm['players.Player']"}),
            'player_3': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'player_3'", 'null': 'True', 'to': u"orm['players.Player']"}),
            'player_4': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'player_4'", 'null': 'True', 'to': u"orm['players.Player']"}),
            'rating': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'update_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'valve_cdn_image': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'valve_cdn_sponsor_image': ('django.db.models.fields.TextField', [], {'null': 'True'})
        }
    }

    complete_apps = ['leagues']