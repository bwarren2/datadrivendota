# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20150420_1410'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Applicant',
        ),
        migrations.RemoveField(
            model_name='permissioncode',
            name='registrant',
        ),
        migrations.DeleteModel(
            name='PollResponse',
        ),
        migrations.DeleteModel(
            name='PermissionCode',
        ),
    ]
