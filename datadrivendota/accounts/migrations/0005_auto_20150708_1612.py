# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20150708_1557'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matchrequest',
            name='match_id',
            field=models.PositiveIntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name='matchrequest',
            name='status',
            field=models.PositiveIntegerField(default=0, choices=[(0, b'Submitted'), (6, b'Finding Match'), (5, b'Match Not Found'), (7, b'Match Found'), (1, b'Replay Available'), (2, b'Replay Not Available'), (3, b'Parsed'), (4, b'Complete')]),
        ),
    ]
