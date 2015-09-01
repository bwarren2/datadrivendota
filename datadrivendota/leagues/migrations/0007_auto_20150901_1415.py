# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0006_auto_20150805_1107'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='league',
            name='valve_cdn_image',
        ),
        migrations.AddField(
            model_name='league',
            name='stored_image',
            field=models.ImageField(null=True, upload_to=b'leagues/img/'),
        ),
    ]
