# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_pingrequest_created'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='matchrequest',
            name='replay_file_url',
        ),
        migrations.AlterField(
            model_name='matchrequest',
            name='raw_parse_url',
            field=models.TextField(null=True, blank=True),
        ),
    ]
