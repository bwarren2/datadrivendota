# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Team'
        db.create_table(u'teams_team', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('steam_id', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('created', self.gf('django.db.models.fields.IntegerField')()),
            ('rating', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('logo', self.gf('django.db.models.fields.BigIntegerField')()),
            ('logo_sponsor', self.gf('django.db.models.fields.BigIntegerField')()),
            ('country_code', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('games_played_with_current_roster', self.gf('django.db.models.fields.IntegerField')()),
            ('player_0', self.gf('django.db.models.fields.related.ForeignKey')(related_name='player_0', to=orm['players.Player'])),
            ('player_1', self.gf('django.db.models.fields.related.ForeignKey')(related_name='player_1', to=orm['players.Player'])),
            ('player_2', self.gf('django.db.models.fields.related.ForeignKey')(related_name='player_2', to=orm['players.Player'])),
            ('player_3', self.gf('django.db.models.fields.related.ForeignKey')(related_name='player_3', to=orm['players.Player'])),
            ('player_4', self.gf('django.db.models.fields.related.ForeignKey')(related_name='player_4', to=orm['players.Player'])),
            ('admin', self.gf('django.db.models.fields.related.ForeignKey')(related_name='team_admin', to=orm['players.Player'])),
        ))
        db.send_create_signal(u'teams', ['Team'])

        # Adding M2M table for field leagues on 'Team'
        m2m_table_name = db.shorten_name(u'teams_team_leagues')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('team', models.ForeignKey(orm[u'teams.team'], null=False)),
            ('league', models.ForeignKey(orm[u'leagues.league'], null=False))
        ))
        db.create_unique(m2m_table_name, ['team_id', 'league_id'])


    def backwards(self, orm):
        # Deleting model 'Team'
        db.delete_table(u'teams_team')

        # Removing M2M table for field leagues on 'Team'
        db.delete_table(db.shorten_name(u'teams_team_leagues'))


    models = {
        u'leagues.league': {
            'Meta': {'object_name': 'League'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_def': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {}),
            'tournament_url': ('django.db.models.fields.CharField', [], {'max_length': '300'})
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
            'admin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'team_admin'", 'to': u"orm['players.Player']"}),
            'country_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'created': ('django.db.models.fields.IntegerField', [], {}),
            'games_played_with_current_roster': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'leagues': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['leagues.League']", 'symmetrical': 'False'}),
            'logo': ('django.db.models.fields.BigIntegerField', [], {}),
            'logo_sponsor': ('django.db.models.fields.BigIntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'player_0': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'player_0'", 'to': u"orm['players.Player']"}),
            'player_1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'player_1'", 'to': u"orm['players.Player']"}),
            'player_2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'player_2'", 'to': u"orm['players.Player']"}),
            'player_3': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'player_3'", 'to': u"orm['players.Player']"}),
            'player_4': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'player_4'", 'to': u"orm['players.Player']"}),
            'rating': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['teams']