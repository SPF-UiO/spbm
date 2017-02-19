# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('norlonn', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='norlonnreport',
            options={'permissions': (('generate_report', 'Can generate norlønn report'), ('view_report', 'Can view norlønn reports'))},
        ),
    ]
