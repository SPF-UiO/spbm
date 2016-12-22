# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_events_change_fkey'),
        ('society', '0005_events_create_state'),
    ]

    database_operations = [
        migrations.AlterModelTable('Event', 'society_event'),
        migrations.AlterModelTable('Shift', 'society_shift')
    ]

    operations = [
        migrations.SeparateDatabaseAndState(database_operations=database_operations)
    ]
