# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserProfile'
        db.create_table(u'accounts_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('player', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['players.Player'], unique=True)),
            ('track_limit', self.gf('django.db.models.fields.IntegerField')(default=7)),
            ('request_limit', self.gf('django.db.models.fields.IntegerField')(default=10)),
        ))
        db.send_create_signal(u'accounts', ['UserProfile'])

        # Adding M2M table for field following on 'UserProfile'
        m2m_table_name = db.shorten_name(u'accounts_userprofile_following')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm[u'accounts.userprofile'], null=False)),
            ('player', models.ForeignKey(orm[u'players.player'], null=False))
        ))
        db.create_unique(m2m_table_name, ['userprofile_id', 'player_id'])

        # Adding M2M table for field tracking on 'UserProfile'
        m2m_table_name = db.shorten_name(u'accounts_userprofile_tracking')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm[u'accounts.userprofile'], null=False)),
            ('player', models.ForeignKey(orm[u'players.player'], null=False))
        ))
        db.create_unique(m2m_table_name, ['userprofile_id', 'player_id'])

        # Adding M2M table for field requested on 'UserProfile'
        m2m_table_name = db.shorten_name(u'accounts_userprofile_requested')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm[u'accounts.userprofile'], null=False)),
            ('matchrequest', models.ForeignKey(orm[u'accounts.matchrequest'], null=False))
        ))
        db.create_unique(m2m_table_name, ['userprofile_id', 'matchrequest_id'])

        # Adding model 'MatchRequest'
        db.create_table(u'accounts_matchrequest', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('match_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
        ))
        db.send_create_signal(u'accounts', ['MatchRequest'])

        # Adding model 'Applicant'
        db.create_table(u'accounts_applicant', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('steam_id', self.gf('django.db.models.fields.BigIntegerField')()),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('interested_in_premium', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'accounts', ['Applicant'])

        # Adding model 'PermissionCode'
        db.create_table(u'accounts_permissioncode', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('key', self.gf('django.db.models.fields.CharField')(default='dd66b4f8-02d9-46d4-bbd7-d23a3c7bffd2', max_length=40)),
            ('registrant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('upgrade_type', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'accounts', ['PermissionCode'])


    def backwards(self, orm):
        # Deleting model 'UserProfile'
        db.delete_table(u'accounts_userprofile')

        # Removing M2M table for field following on 'UserProfile'
        db.delete_table(db.shorten_name(u'accounts_userprofile_following'))

        # Removing M2M table for field tracking on 'UserProfile'
        db.delete_table(db.shorten_name(u'accounts_userprofile_tracking'))

        # Removing M2M table for field requested on 'UserProfile'
        db.delete_table(db.shorten_name(u'accounts_userprofile_requested'))

        # Deleting model 'MatchRequest'
        db.delete_table(u'accounts_matchrequest')

        # Deleting model 'Applicant'
        db.delete_table(u'accounts_applicant')

        # Deleting model 'PermissionCode'
        db.delete_table(u'accounts_permissioncode')


    models = {
        u'accounts.applicant': {
            'Meta': {'object_name': 'Applicant'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interested_in_premium': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'steam_id': ('django.db.models.fields.BigIntegerField', [], {})
        },
        u'accounts.matchrequest': {
            'Meta': {'object_name': 'MatchRequest'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        u'accounts.permissioncode': {
            'Meta': {'object_name': 'PermissionCode'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'default': "'9ddc6e63-089f-4262-8857-1ad7b18d81c0'", 'max_length': '40'}),
            'registrant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            'upgrade_type': ('django.db.models.fields.IntegerField', [], {})
        },
        u'accounts.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'following': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'quarry'", 'symmetrical': 'False', 'to': u"orm['players.Player']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['players.Player']", 'unique': 'True'}),
            'request_limit': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'requested': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['accounts.MatchRequest']", 'null': 'True', 'symmetrical': 'False'}),
            'track_limit': ('django.db.models.fields.IntegerField', [], {'default': '7'}),
            'tracking': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'feed'", 'symmetrical': 'False', 'to': u"orm['players.Player']"}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
        }
    }

    complete_apps = ['accounts']