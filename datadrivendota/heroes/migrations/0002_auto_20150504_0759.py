# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heroes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ability',
            name='machine_name',
            field=models.CharField(help_text=b"Valve's underscore name, slugified", max_length=150),
        ),
    ]
