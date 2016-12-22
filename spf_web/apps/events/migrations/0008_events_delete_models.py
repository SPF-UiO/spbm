# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_events_database_alter'),
    ]

    state_operations = [
        migrations.RemoveField(
            model_name='event',
            name='invoice',
        ),
        migrations.RemoveField(
            model_name='event',
            name='society',
        ),
        migrations.AlterUniqueTogether(
            name='shift',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='shift',
            name='event',
        ),
        migrations.RemoveField(
            model_name='shift',
            name='norlonn_report',
        ),
        migrations.RemoveField(
            model_name='shift',
            name='worker',
        ),
        migrations.DeleteModel(
            name='Event',
        ),
        migrations.DeleteModel(
            name='Shift',
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]
