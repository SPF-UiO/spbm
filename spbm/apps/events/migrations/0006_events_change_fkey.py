# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('society', '0005_events_create_state'),
        ('events', '0005_auto_20161218_1500'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shift',
            name='event',
            field=models.ForeignKey(to='society.Event'),
        ),
    ]
