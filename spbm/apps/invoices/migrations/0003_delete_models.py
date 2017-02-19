# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('invoices', '0002_alter_table'),
    ]

    state_operations = [
        migrations.AlterUniqueTogether(
            name='invoice',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='society',
        ),
        migrations.DeleteModel(
            name='Invoice',
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]
