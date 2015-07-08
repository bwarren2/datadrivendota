# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0003_auto_20150627_1200'),
    ]

    operations = [
        migrations.AddField(
            model_name='matchrequest',
            name='creation',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 8, 19, 56, 56, 333243, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='matchrequest',
            name='last_modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 8, 19, 57, 1, 208790, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='matchrequest',
            name='raw_parse_url',
            field=models.URLField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='matchrequest',
            name='replay_file_url',
            field=models.URLField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='matchrequest',
            name='requester',
            field=models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='matchrequest',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, b'Submitted'), (6, b'Finding Match'), (5, b'Match Not Found'), (7, b'Match Found'), (1, b'Replay Available'), (2, b'Replay Not Available'), (3, b'Parsed'), (4, b'Complete')]),
        ),
        migrations.AddField(
            model_name='matchrequest',
            name='valve_replay_url',
            field=models.URLField(null=True, blank=True),
        ),
    ]
