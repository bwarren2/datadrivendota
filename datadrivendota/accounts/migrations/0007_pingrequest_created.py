# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_pingrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='pingrequest',
            name='created',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
