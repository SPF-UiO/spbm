# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workers', '0002_auto_20161218_1136'),
    ]

    state_operations = [
        migrations.DeleteModel('Worker')
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]
