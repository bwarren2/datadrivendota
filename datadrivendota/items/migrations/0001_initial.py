# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('steam_id', models.IntegerField(help_text=b"Valve's normalization id", unique=True)),
                ('thumbshot', models.ImageField(upload_to=b'items/img/')),
                ('mugshot', models.ImageField(upload_to=b'items/img/')),
                ('name', models.CharField(help_text=b'The name for people', max_length=100)),
                ('internal_name', models.CharField(help_text=b'The underscore name', max_length=100)),
                ('quality', models.CharField(help_text=b'Internal shop category name', max_length=100)),
                ('cost', models.IntegerField(default=0, null=True)),
                ('description', models.TextField(null=True)),
                ('notes', models.TextField(null=True)),
                ('mana_cost', models.IntegerField(null=True)),
                ('cooldown', models.IntegerField(null=True)),
                ('lore', models.TextField(null=True)),
                ('created', models.NullBooleanField()),
                ('slug_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ItemAttributes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attribute', models.CharField(max_length=100)),
                ('item', models.ForeignKey(to='items.Item')),
            ],
        ),
        migrations.CreateModel(
            name='ItemComponents',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ingredient', models.ForeignKey(related_name='ingredients', to='items.Item')),
                ('product', models.ForeignKey(related_name='product', to='items.Item')),
            ],
        ),
    ]
