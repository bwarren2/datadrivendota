# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import blog.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.CharField(default=b'', max_length=200)),
                ('content', models.TextField()),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', blog.fields.AutoDatetimeField(default=django.utils.timezone.now)),
                ('publicity', models.IntegerField(default=2, choices=[(0, b'Public'), (1, b'Login'), (2, b'Private')])),
            ],
            options={
                'verbose_name_plural': 'entries',
            },
        ),
    ]
