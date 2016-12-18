# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workers', '0001_initial'),
        ('society', '0004_worker')
    ]

    database_operations = [
        migrations.AlterModelTable('Worker', 'society_worker')
    ]

    state_operations = [
        # migrations.DeleteModel('Worker')
    ]

    operations = [
        migrations.SeparateDatabaseAndState(database_operations=database_operations,
                                            state_operations=state_operations)
    ]
