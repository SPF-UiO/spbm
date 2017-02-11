# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Migration of workers_worker to society_worker in the database.
    1/3
    """

    dependencies = [
        ('workers', '0001_initial'),
    ]

    database_operations = [
        migrations.AlterModelTable('Worker', 'society_worker')
    ]

    operations = [
        migrations.SeparateDatabaseAndState(database_operations=database_operations)
    ]
