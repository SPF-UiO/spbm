# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_auto_20161218_1500'),
    ]

    database_operations = [
        migrations.AlterModelTable('Event', 'society_event'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(database_operations=database_operations)
    ]
