# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0003_auto_20150530_1151'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='logo_sponsor',
        ),
        migrations.RemoveField(
            model_name='team',
            name='valve_cdn_sponsor_image',
        ),
        migrations.AddField(
            model_name='team',
            name='stored_image',
            field=models.ImageField(null=True, upload_to=b'teams/img/'),
        ),
    ]
