# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'TeamDossier'
        db.delete_table(u'teams_teamdossier')

        # Removing M2M table for field leagues on 'TeamDossier'
        db.delete_table(db.shorten_name(u'teams_teamdossier_leagues'))

        # Adding field 'Team.name'
        db.add_column(u'teams_team', 'name',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True),
                      keep_default=False)

        # Adding field 'Team.tag'
        db.add_column(u'teams_team', 'tag',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True),
                      keep_default=False)

        # Adding field 'Team.created'
        db.add_column(u'teams_team', 'created',
                      self.gf('django.db.models.fields.IntegerField')(null=True),
                      keep_default=False)

        # Adding field 'Team.rating'
        db.add_column(u'teams_team', 'rating',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True),
                      keep_default=False)

        # Adding field 'Team.logo'
        db.add_column(u'teams_team', 'logo',
                      self.gf('django.db.models.fields.BigIntegerField')(null=True),
                      keep_default=False)

        # Adding field 'Team.logo_sponsor'
        db.add_column(u'teams_team', 'logo_sponsor',
                      self.gf('django.db.models.fields.BigIntegerField')(null=True),
                      keep_default=False)

        # Adding field 'Team.country_code'
        db.add_column(u'teams_team', 'country_code',
                      self.gf('django.db.models.fields.CharField')(max_length=10, null=True),
                      keep_default=False)

        # Adding field 'Team.url'
        db.add_column(u'teams_team', 'url',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True),
                      keep_default=False)

        # Adding field 'Team.games_played_with_current_roster'
        db.add_column(u'teams_team', 'games_played_with_current_roster',
                      self.gf('django.db.models.fields.IntegerField')(null=True),
                      keep_default=False)

        # Adding field 'Team.player_0'
        db.add_column(u'teams_team', 'player_0',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='player_0', null=True, to=orm['players.Player']),
                      keep_default=False)

        # Adding field 'Team.player_1'
        db.add_column(u'teams_team', 'player_1',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='player_1', null=True, to=orm['players.Player']),
                      keep_default=False)

        # Adding field 'Team.player_2'
        db.add_column(u'teams_team', 'player_2',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='player_2', null=True, to=orm['players.Player']),
                      keep_default=False)

        # Adding field 'Team.player_3'
        db.add_column(u'teams_team', 'player_3',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='player_3', null=True, to=orm['players.Player']),
                      keep_default=False)

        # Adding field 'Team.player_4'
        db.add_column(u'teams_team', 'player_4',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='player_4', null=True, to=orm['players.Player']),
                      keep_default=False)

        # Adding field 'Team.admin'
        db.add_column(u'teams_team', 'admin',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='team_admin', null=True, to=orm['players.Player']),
                      keep_default=False)

        # Adding field 'Team.logo_image'
        db.add_column(u'teams_team', 'logo_image',
                      self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True),
                      keep_default=False)

        # Adding field 'Team.logo_sponsor_image'
        db.add_column(u'teams_team', 'logo_sponsor_image',
                      self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True),
                      keep_default=False)

        # Adding field 'Team.update_time'
        db.add_column(u'teams_team', 'update_time',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)

        # Adding M2M table for field leagues on 'Team'
        m2m_table_name = db.shorten_name(u'teams_team_leagues')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('team', models.ForeignKey(orm[u'teams.team'], null=False)),
            ('league', models.ForeignKey(orm[u'leagues.league'], null=False))
        ))
        db.create_unique(m2m_table_name, ['team_id', 'league_id'])


    def backwards(self, orm):
        # Adding model 'TeamDossier'
        db.create_table(u'teams_teamdossier', (
            ('rating', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('country_code', self.gf('django.db.models.fields.CharField')(max_length=10, null=True)),
            ('logo', self.gf('django.db.models.fields.BigIntegerField')(null=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('logo_sponsor_image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True)),
            ('player_4', self.gf('django.db.models.fields.related.ForeignKey')(related_name='player_4', null=True, to=orm['players.Player'])),
            ('player_2', self.gf('django.db.models.fields.related.ForeignKey')(related_name='player_2', null=True, to=orm['players.Player'])),
            ('player_3', self.gf('django.db.models.fields.related.ForeignKey')(related_name='player_3', null=True, to=orm['players.Player'])),
            ('player_0', self.gf('django.db.models.fields.related.ForeignKey')(related_name='player_0', null=True, to=orm['players.Player'])),
            ('player_1', self.gf('django.db.models.fields.related.ForeignKey')(related_name='player_1', null=True, to=orm['players.Player'])),
            ('games_played_with_current_roster', self.gf('django.db.models.fields.IntegerField')()),
            ('update_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('logo_image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('created', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('admin', self.gf('django.db.models.fields.related.ForeignKey')(related_name='team_admin', null=True, to=orm['players.Player'])),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('logo_sponsor', self.gf('django.db.models.fields.BigIntegerField')(null=True)),
            ('team', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['teams.Team'], unique=True)),
        ))
        db.send_create_signal(u'teams', ['TeamDossier'])

        # Adding M2M table for field leagues on 'TeamDossier'
        m2m_table_name = db.shorten_name(u'teams_teamdossier_leagues')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('teamdossier', models.ForeignKey(orm[u'teams.teamdossier'], null=False)),
            ('league', models.ForeignKey(orm[u'leagues.league'], null=False))
        ))
        db.create_unique(m2m_table_name, ['teamdossier_id', 'league_id'])

        # Deleting field 'Team.name'
        db.delete_column(u'teams_team', 'name')

        # Deleting field 'Team.tag'
        db.delete_column(u'teams_team', 'tag')

        # Deleting field 'Team.created'
        db.delete_column(u'teams_team', 'created')

        # Deleting field 'Team.rating'
        db.delete_column(u'teams_team', 'rating')

        # Deleting field 'Team.logo'
        db.delete_column(u'teams_team', 'logo')

        # Deleting field 'Team.logo_sponsor'
        db.delete_column(u'teams_team', 'logo_sponsor')

        # Deleting field 'Team.country_code'
        db.delete_column(u'teams_team', 'country_code')

        # Deleting field 'Team.url'
        db.delete_column(u'teams_team', 'url')

        # Deleting field 'Team.games_played_with_current_roster'
        db.delete_column(u'teams_team', 'games_played_with_current_roster')

        # Deleting field 'Team.player_0'
        db.delete_column(u'teams_team', 'player_0_id')

        # Deleting field 'Team.player_1'
        db.delete_column(u'teams_team', 'player_1_id')

        # Deleting field 'Team.player_2'
        db.delete_column(u'teams_team', 'player_2_id')

        # Deleting field 'Team.player_3'
        db.delete_column(u'teams_team', 'player_3_id')

        # Deleting field 'Team.player_4'
        db.delete_column(u'teams_team', 'player_4_id')

        # Deleting field 'Team.admin'
        db.delete_column(u'teams_team', 'admin_id')

        # Deleting field 'Team.logo_image'
        db.delete_column(u'teams_team', 'logo_image')

        # Deleting field 'Team.logo_sponsor_image'
        db.delete_column(u'teams_team', 'logo_sponsor_image')

        # Deleting field 'Team.update_time'
        db.delete_column(u'teams_team', 'update_time')

        # Removing M2M table for field leagues on 'Team'
        db.delete_table(db.shorten_name(u'teams_team_leagues'))


    models = {
        u'leagues.league': {
            'Meta': {'object_name': 'League'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_def': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'logo_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'steam_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'tournament_url': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True'}),
            'update_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
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
            'logo_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
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
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'})
        }
    }

    complete_apps = ['teams']