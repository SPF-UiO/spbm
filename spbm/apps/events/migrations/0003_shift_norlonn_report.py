# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('norlonn', '0001_initial'),
        ('events', '0002_auto_20150304_2018'),
    ]

    operations = [
        migrations.AddField(
            model_name='shift',
            name='norlonn_report',
            field=models.ForeignKey(to='norlonn.NorlonnReport', null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
    ]
