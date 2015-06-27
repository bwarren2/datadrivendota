# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0002_auto_20150507_0953'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pickban',
            options={'ordering': ['match', 'order']},
        ),
    ]
